

from dlqyoutubedl import DLQYouTubeDl
from dlqmaildirstore import DLQMaildirStore
from dlqtransaction import DLQTransaction
import json

dlq_store = DLQMaildirStore('./queue')
dl = DLQYouTubeDl()

(queue_item_path, queue_item) = dlq_store.new_item()
print(f"queue_item: {queue_item}")
if queue_item:
    trans = DLQTransaction()
    trans["queue_item"] = queue_item
    print(f"queue_item_path: {queue_item_path}")
    tmp_item_path = dlq_store.lock_file(queue_item_path)
    print(f"tmp_item_path: {tmp_item_path}")
    if tmp_item_path:
        trans["tmp_item_path"] = str(tmp_item_path)
        trans["state"] = 10
        trans.write()
        trans["dlresult"] = dl.download(queue_item["url"])
        if trans["dlresult"]["returncode"] == 0:
            trans["state"] = 20
            trans.write()
            cur_item_path = dlq_store.file_done(tmp_item_path)
            if cur_item_path:
                trans["state"] = 30
                trans["cur_item_path"] = str(cur_item_path)
                trans.write()
        else:
            trans["state"] = 40
            trans.write()
            err_item_path = dlq_store.file_had_errors(tmp_item_path)
            if err_item_path:
                trans["state"] = 50
                trans["err_item_path"] = str(err_item_path)
                trans.write()
