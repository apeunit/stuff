#!/usr/bin/env python3
import argparse
import csv
import json


def tg_links(in_file, out_file):
    csv_fp = open(out_file, "w")
    fieldnames = ['date', 'user', 'url']
    csv_w = csv.DictWriter(csv_fp, fieldnames=fieldnames)
    csv_w.writeheader()
    # count links found
    count_l = 0
    # parse the file
    with open(in_file) as fp:
        data = json.load(fp)
        msgs = data.get("messages", [])
        name, count_m = data.get("name"), len(msgs)
        print(f"Parsing export for {name} with {count_m} messages")
        for m in msgs:
            # we are interested in messages
            if m.get("type", "?") != "message":
                continue
            # get the date and the user
            record = {
                "date": m.get("date"),
                "user": m.get("from")
            }
            # get the text
            text = m.get("text", [])
            # texts can be string or list, we are interested in lists
            if not isinstance(text, list):
                continue
            for e in text:
                # we are interested in dict objects
                if not isinstance(e, dict):
                    continue
                # we are interested in link types
                if e.get("type", "?") != "link":
                    continue
                # here there is what we are looking for
                record["url"] = e.get("text")
                csv_w.writerow(record)
                count_l += 1

    print(f"Csv export completed to {out_file}, found {count_l} links")
    csv_fp.flush()
    csv_fp.close()


def cmd_links(args):
    out_file = f"{args.file}.csv"
    tg_links(args.file, out_file)


if __name__ == '__main__':
    cmds = [
        {
            'name': 'csv',
            'help': 'extract the links from a telegram json history export into a csv file',
            'opts': [
                {
                    'names': ['-f', '--file'],
                    'help':'telegram log file to parse (default result.json)',
                    'default': "result.json",
                }
            ],
            'target': cmd_links
        },
    ]
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    subparsers.required = True
    subparsers.dest = 'command'
    # register all the commands
    for c in cmds:
        subp = subparsers.add_parser(c['name'], help=c['help'])
        subp.set_defaults(func=c['target'])
        # add the sub arguments
        for sa in c.get('opts', []):
            subp.add_argument(*sa['names'],
                              help=sa['help'],
                              action=sa.get('action'),
                              default=sa.get('default'),
                              required=sa.get('required', False))

    # parse the arguments
    args = parser.parse_args()
    # call the function
    args.func(args)
