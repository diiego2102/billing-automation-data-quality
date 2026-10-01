"""Deterministic billing preparation demo. Fictional accounts and demonstration rates.

Amounts are draft calculations only: no tax, real tariff, invoicing API or network.
"""
from collections import Counter, defaultdict
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
from pathlib import Path
import csv
import json
import random

ROOT=Path(__file__).resolve().parent
PERIOD='2026-09'
START='2026-09-01';END='2026-10-01'
RATE=Decimal('0.18');FIXED=Decimal('4.50')
MONEY=Decimal('0.01')


def generate(seed=26,n_accounts=100):
    rng=random.Random(seed);rows=[]
    for i in range(n_accounts):
        start=Decimal(rng.randrange(1000,10000));usage=Decimal(rng.randrange(100,850))
        for day,value in [(START,start),(END,start+usage)]:
            rows.append(dict(account_id=f'DEMO-{i+1:04}',reading_date=day,cumulative_units=str(value)))
    # Explicit defects: duplicate endpoint, absent endpoint, negative delta,
    # extreme delta, and a non-numeric endpoint. These accounts must be held.
    rows.append(dict(rows[1]));rows=[r for r in rows if not(r['account_id']=='DEMO-0002' and r['reading_date']==END)]
    for r in rows:
        if r['account_id']=='DEMO-0003' and r['reading_date']==END:r['cumulative_units']='1'
        if r['account_id']=='DEMO-0004' and r['reading_date']==END:r['cumulative_units']='999999'
        if r['account_id']=='DEMO-0005' and r['reading_date']==END:r['cumulative_units']='unknown'
    return rows


def prepare(rows,max_units=Decimal('2000')):
    """Gate draft billing on exactly one valid reading at each period boundary.

    This demo assumes cumulative meters with no reset/rollover. Such cases are
    held for review, never automatically corrected or estimated.
    """
    grouped=defaultdict(list)
    for row in rows:
        if not row.get('account_id'):
            raise ValueError('Every record must have an account_id; no silent orphan drop.')
        grouped[row['account_id']].append(row)
    drafts=[];exceptions=[]
    for account,records in sorted(grouped.items()):
        issues=[];counts=Counter(r.get('reading_date') for r in records)
        for day in (START,END):
            if counts[day]==0:issues.append('missing_boundary')
            elif counts[day]>1:issues.append('duplicate_boundary')
        if any(day not in (START,END) for day in counts):issues.append('unexpected_date')
        values={}
        for r in records:
            try:
                value=Decimal(str(r.get('cumulative_units','')))
                if not value.is_finite() or value<0:raise InvalidOperation
                values[r.get('reading_date')]=value
            except (InvalidOperation,ValueError):issues.append('invalid_reading')
        consumption=None
        if not issues:
            consumption=values[END]-values[START]
            if consumption<0:issues.append('negative_delta_or_reset')
            elif consumption>max_units:issues.append('high_consumption_review')
        if issues:
            exceptions.append(dict(account_id=account,period=PERIOD,status='HOLD',
                reasons=';'.join(sorted(set(issues)))))
            continue
        variable=(consumption*RATE).quantize(MONEY,rounding=ROUND_HALF_UP)
        total=(variable+FIXED).quantize(MONEY,rounding=ROUND_HALF_UP)
        drafts.append(dict(account_id=account,period=PERIOD,status='DRAFT',
            consumption_units=str(consumption),unit_rate=str(RATE),fixed_charge=str(FIXED),
            variable_charge=str(variable),total_before_tax=str(total)))
    assert len(drafts)+len(exceptions)==len(grouped)
    assert not ({d['account_id'] for d in drafts}&{e['account_id'] for e in exceptions})
    summary=dict(period=PERIOD,source_records=len(rows),accounts=len(grouped),
        draft_accounts=len(drafts),held_accounts=len(exceptions),
        total_before_tax=str(sum((Decimal(d['total_before_tax']) for d in drafts),Decimal(0)).quantize(MONEY)),
        synthetic_only=True)
    return drafts,exceptions,summary


def write_csv(path,rows,fields):
    with path.open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader();writer.writerows(rows)


def main():
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input',type=Path,help='CSV with account_id,reading_date,cumulative_units; same demo boundaries and rates.')
    args=parser.parse_args()
    if args.input:
        with args.input.open(newline='',encoding='utf-8') as f:
            reader=csv.DictReader(f)
            if not {'account_id','reading_date','cumulative_units'}<=set(reader.fieldnames or []):
                raise ValueError('Input CSV is missing required columns.')
            rows=list(reader)
    else:rows=generate()
    drafts,exceptions,summary=prepare(rows)
    out=ROOT/'outputs';out.mkdir(exist_ok=True)
    write_csv(out/'synthetic_input.csv',rows,['account_id','reading_date','cumulative_units'])
    write_csv(out/'billing_drafts.csv',drafts,['account_id','period','status','consumption_units','unit_rate','fixed_charge','variable_charge','total_before_tax'])
    write_csv(out/'exceptions.csv',exceptions,['account_id','period','status','reasons'])
    (out/'run_summary.json').write_text(json.dumps(summary,indent=2))
    print(json.dumps(summary,indent=2));print('Drafts only. Review holds before billing. No real invoices are issued.')


if __name__=='__main__':main()
