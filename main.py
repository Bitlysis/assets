import json
from asyncio import run
from dataclasses import dataclass
from os import getenv
from pathlib import Path

import aiofiles
from aiobotocore.session import get_session


DEFAULT_MAPPING = json.dumps({
    'ethereum': 'eth',
    'polygon': 'polygon',
    'tron': 'tron',
})


class Env:
    AWS_REGION: str = getenv('AWS_REGION')
    AWS_ACCESS_KEY_ID: str = getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY: str = getenv('AWS_SECRET_ACCESS_KEY')
    AWS_BUCKET: str = getenv('AWS_BUCKET')
    MAPPING: dict[str, str] = json.loads(getenv('MAPPING', DEFAULT_MAPPING))


async def read_and_upload(
        file_path: Path,
        chain: str,
        address: str,
        client,
):
    async with aiofiles.open(str(file_path), mode='rb') as f:
        data = await f.read()
        await client.put_object(
            Body=data,
            Bucket=Env.AWS_BUCKET,
            Key=f'icons/{chain}/{address}.png',
            ContentType="image/png",
        )


@dataclass
class FileToUpload:
    path: Path
    chain: str
    address: str


async def main_async(files: list[FileToUpload]):
    session = get_session()
    async with session.create_client(
        's3',
        region_name=Env.AWS_REGION,
        aws_access_key_id=Env.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=Env.AWS_SECRET_ACCESS_KEY,
    ) as client:
        count = len(files)
        for index, file_to_upload in enumerate(files, start=1):
            print(f'Uploading [{index}/{count}] {file_to_upload.chain} {file_to_upload.address}')
            await read_and_upload(
                file_path=file_to_upload.path,
                chain=file_to_upload.chain,
                address=file_to_upload.address,
                client=client,
            )


def main_sync():
    base = Path('blockchains')

    files = [
        FileToUpload(
            path=full_path,
            chain=target,
            address=str(full_path).split('/')[-2],
        )
        for source, target in Env.MAPPING.items()
        for full_path in (base / source).rglob('logo.png')

    ]
    run(main_async(files=files))


if __name__ == '__main__':
    main_sync()
