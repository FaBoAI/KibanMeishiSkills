#!/usr/bin/env python3
"""Check EasyEDA NFC card order files. Standard library only; no uploads."""
import argparse
import csv
import io
import json
import math
from pathlib import Path
import re
import sys
import zipfile


def read_table(path):
    raw = path.read_bytes()
    encoding = 'utf-16' if raw.startswith((b'\xff\xfe', b'\xfe\xff')) else 'utf-8-sig'
    text = raw.decode(encoding)
    dialect = csv.Sniffer().sniff(text, delimiters=',\t')
    reader = csv.DictReader(io.StringIO(text), dialect=dialect)
    fields = reader.fieldnames
    if not fields or len(set(fields)) != len(fields):
        raise ValueError(f'{path.name}: missing or duplicate column headings')
    rows = list(reader)
    if not rows or any(None in row or any(v is None for v in row.values()) for row in rows):
        raise ValueError(f'{path.name}: empty or malformed table')
    return fields, rows


def require(fields, names, label):
    missing = set(names) - set(fields)
    if missing:
        raise ValueError(f'{label}: missing columns {sorted(missing)}')


def number(value, coordinate=False):
    pattern = r'([-+]?\d+(?:\.\d+)?)(?:\s*(mm|mil))?' if coordinate else r'([-+]?\d+(?:\.\d+)?)'
    match = re.fullmatch(pattern, value.strip(), re.I)
    if not match or not math.isfinite(float(match[1])):
        raise ValueError(f'invalid number/unit: {value!r}')
    return float(match[1])


def run(args):
    bf, br = read_table(args.bom)
    cf, cr = read_table(args.cpl)
    require(bf, ['Designator', 'Quantity', 'Supplier Part', 'Manufacturer Part'], 'BOM')
    require(cf, ['Designator', 'Mid X', 'Mid Y', 'Layer', 'Rotation'], 'CPL')
    bom_refs = set()
    parts = []
    for row in br:
        refs = [x for x in re.split(r'[,;\s]+', row['Designator'].strip()) if x]
        if not refs or len(set(refs)) != len(refs) or bom_refs.intersection(refs):
            raise ValueError('BOM: empty or duplicate designator')
        qty = number(row['Quantity'])
        if qty != len(refs):
            raise ValueError(f'BOM: quantity does not match designators {refs}')
        if not re.fullmatch(r'C\d+', row['Supplier Part'].strip()) or not row['Manufacturer Part'].strip():
            raise ValueError(f'BOM: missing/invalid supplier or manufacturer part for {refs}')
        bom_refs.update(refs)
        parts.append({'designators': refs, 'supplier_part': row['Supplier Part'], 'mpn': row['Manufacturer Part']})
    cpl_refs = set()
    for row in cr:
        ref = row['Designator'].strip()
        if not ref or ref in cpl_refs:
            raise ValueError('CPL: empty or duplicate designator')
        cpl_refs.add(ref)
        for key in ['Mid X', 'Mid Y']:
            number(row[key], coordinate=True)
        number(row['Rotation'])
        if row['Layer'].strip().lower() not in {'t', 'b', 'top', 'bottom', 'toplayer', 'bottomlayer'}:
            raise ValueError(f'CPL: unknown layer for {ref}')
    if bom_refs != cpl_refs:
        raise ValueError(f'BOM/CPL mismatch: BOM-only={sorted(bom_refs-cpl_refs)}, CPL-only={sorted(cpl_refs-bom_refs)}')
    with zipfile.ZipFile(args.gerber) as z:
        bad = z.testzip()
        if bad:
            raise ValueError(f'ZIP CRC failure: {bad}')
        names = z.namelist()
        for ext in ['.GTL', '.GBL', '.GKO', '.FCTS', '.FCBO']:
            matches = [n for n in names if n.upper().endswith(ext)]
            if len(matches) != 1 or not z.getinfo(matches[0]).file_size:
                raise ValueError(f'Gerber: expected one nonempty {ext} file')
    if args.normalized_dir:
        args.normalized_dir.mkdir(parents=True, exist_ok=True)
        for name, fields, rows in [('BOM.csv', bf, br), ('CPL.csv', cf, cr)]:
            target = args.normalized_dir / name
            if target.resolve() in {args.bom.resolve(), args.cpl.resolve()} or target.exists():
                raise ValueError(f'refusing to overwrite {target}')
        for name, fields, rows in [('BOM.csv', bf, br), ('CPL.csv', cf, cr)]:
            with (args.normalized_dir / name).open('x', encoding='utf-8-sig', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fields)
                writer.writeheader()
                writer.writerows(rows)
    return {'format_checks': 'passed', 'parts': parts, 'placements': len(cr),
            'limits': 'Does not verify DRC, geometry, polarity, stock, RF performance or order status.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for option in ['bom', 'cpl', 'gerber']:
        parser.add_argument('--' + option, type=Path, required=True)
    parser.add_argument('--normalized-dir', type=Path)
    try:
        print(json.dumps(run(parser.parse_args()), ensure_ascii=False, indent=2))
    except (ValueError, OSError, UnicodeError, csv.Error, zipfile.BadZipFile) as exc:
        print(f'ERROR: {exc}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
