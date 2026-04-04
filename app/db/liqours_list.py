from app.utils.genutils import safe_get
from file_reader.json_reader import JsonReader


def read_ksbcl(file_path):
    json_reader = JsonReader()
    json_data = json_reader.read(file_path)
    return safe_get(json_data, 'data', [])


def to_float(value, default=0):
    try:
        return float(str(value).replace(",", ""))
    except (ValueError, TypeError):
        return default


def update_db(records):
    from app.config.database_session_provider import get_provider
    from app.config import _config
    config_details = _config.PRIMARY_CONFIG
    provider = get_provider(config_details)
    from app.db.liquor_list.model import LiquorList
    new_record = []
    for record in records:
        liquor_list = LiquorList()
        liquor_list.item_name = safe_get(record, 's', defaultValue='')
        liquor_list.qty = safe_get(record, 'qty', 0)
        if not liquor_list.qty:
            liquor_list.qty = 0
        liquor_list.mrp = to_float(safe_get(record, 'MRP', 0))
        liquor_list.kscl_price = to_float(safe_get(record, 'KSBCL SELLING PRICE', defaultValue=0))
        new_record.append(liquor_list)

    provider.save_all(new_record)


def upload_ksbl(file_path):
    json_data = read_ksbcl(file_path)
    update_db(json_data)


if __name__ == '__main__':
    upload_ksbl(
        file_path=rf"D:\office\code\spirix resource\processed\processed\master-ksbcl.json"
    )
