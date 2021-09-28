from dotenv import dotenv_values
import requests
from typing import Dict, List
import json
import argparse


class CloudFlareRequests:
    def __init__(self, cli_args) -> None:
        config = dotenv_values(cli_args["config"])
        self.API_KEY = cli_args["apikey"] if cli_args["apikey"] is not None else config["API_KEY"]
        self.ZONE = cli_args["zone"] if cli_args["zone"] is not None else config["ZONE"]
        self.DEFAULT_HEADERS = {"Authorization": f"Bearer {self.API_KEY}",
                                "Content-Type": "application/json"}

    def __repr__(self) -> str:
        return f"CloudFlareRequests{self.API_KEY, self.ZONE}"

    def __str__(self) -> str:
        return f"API Key: {self.API_KEY}\nZone: {self.ZONE}"

    def getDNSRecords(self, filterType: str = None, per_page: int = 3) -> List[Dict]:
        res = []

        headers = {
            **self.DEFAULT_HEADERS
        }

        page: int = 1
        per_page: int = per_page

        while True:

            url = f"https://api.cloudflare.com/client/v4/zones/{self.ZONE}/dns_records?page={page}&per_page={per_page}"

            if filterType is not None:
                url += f"&type={filterType}"

            r = requests.get(
                url=url, headers=headers)

            request_json = r.json()

            res.extend(request_json["result"])

            if request_json["result_info"]["count"] < per_page:
                break

            page += 1

        return res

    def updateDNSRecords(self, records: List[Dict], ip: str):
        for record in records:
            record_id = record["id"]
            url = f"https://api.cloudflare.com/client/v4/zones/{self.ZONE}/dns_records/{record_id}"
            headers = {
                **self.DEFAULT_HEADERS,
            }
            data = {
                "type": record["type"],
                "name": record["name"],
                "content": ip,
                "ttl": "1",
                "proxied": record["proxied"]
            }

            r = requests.put(url=url, headers=headers, data=json.dumps(data))

            print(r.json())


def getIPAddress() -> str:
    ip = requests.get('https://api.ipify.org').text
    return ip


def main():
    parser = argparse.ArgumentParser(
        description="CLourdFlare API to Update IP Address for Records"
    )

    parser.add_argument(
        "-c",
        "--config",
        dest="config",
        type=str,
        help="The File Path to the .dotenv Config File",
        required=True)

    parser.add_argument(
        "-z",
        "--zone",
        dest="zone",
        type=str,
        help="The Zone to update",
        required=False)

    parser.add_argument(
        "-a",
        "--apikey",
        dest="apikey",
        type=str,
        help="The API Key to use",
        required=False)

    args = vars(parser.parse_args())

    CFRequests = CloudFlareRequests(args)
    records = CFRequests.getDNSRecords(filterType="A")
    ip = getIPAddress()
    CFRequests.updateDNSRecords(records, ip)


if __name__ in ("__main__"):
    main()
