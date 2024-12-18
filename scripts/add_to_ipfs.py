import subprocess

TOTAL_ZOMBITS = 10_000

with open('zombits_ipfs.csv', 'a') as outfile:
    for i in range(TOTAL_ZOMBITS):
        zombit_id = i+1
        ipfs_add = subprocess.run(["ipfs", "add", f"Final/Zombit{zombit_id}.png"], check=True, capture_output=True)
        print(ipfs_add.stdout)
        outfile.write(f"{zombit_id},{ipfs_add.stdout.decode('utf-8')}")
