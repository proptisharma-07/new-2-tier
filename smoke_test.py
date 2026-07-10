import os
import sys
import boto3
import pymysql

# SSM Client
client = boto3.client("ssm", region_name="eu-north-1")

# Read parameters from Parameter Store
params = {
    os.path.basename(p["Name"]): p["Value"].strip()
    for p in client.get_parameters_by_path(
        Path="/application/banking",
        WithDecryption=True
    )["Parameters"]
}

required = [
    "DB_HOST",
    "DB_NAME",
    "DB_USER",
    "DB_PASSWORD",
    "DB_PORT"
]

missing = [k for k in required if k not in params]

print("Checking required parameters...\n")

for k in required:
    if k in params:
        print(f"{k} ✅")
    else:
        print(f"{k} ❌")

if missing:
    print(f"\nMissing Parameters: {missing}")
    sys.exit(1)

print("\nDatabase Host:", params["DB_HOST"])

try:
    connection = pymysql.connect(
        host=params["DB_HOST"],
        user=params["DB_USER"],
        password=params["DB_PASSWORD"],
        database=params["DB_NAME"],
        port=int(params["DB_PORT"]),
        connect_timeout=10
    )

    cursor = connection.cursor()

    cursor.execute("SHOW TABLES;")
    tables = [row[0] for row in cursor.fetchall()]

    print(f"\nDatabase : {params['DB_NAME']}")
    print(f"Tables   : {tables}")

    cursor.close()
    connection.close()

except Exception as e:
    print(f"\nDB ERROR ❌: {e}")
    sys.exit(1)

print("\n✅ Smoke Test Passed")