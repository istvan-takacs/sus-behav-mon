from reading_logs import pyparsing_logs, pyparsing_logs_network

def get_logs():
    log1 =  pyparsing_logs.pyparse_logs()
    log2 = pyparsing_logs_network.pyparse_logs()
    logs = log1 + log2

    for idx, log in enumerate(logs, 1):
        log["_id"] = str(idx)

    return logs
