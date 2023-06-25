import pandas as pd
from datetime import datetime
from git import Repo
from app_config import MongoConfig, git_path


if __name__ == '__main__':

    PATH_OF_GIT_REPO = git_path # make sure .git folder is properly configured
    COMMIT_MESSAGE = "[bot] commit"
    repo = Repo(PATH_OF_GIT_REPO)
    origin = repo.remote(name="origin")
    origin.pull("main")


    ids = ['TNB MK Equity', 'YTLP MK Equity', 'SOLAR MK Equity', 'CYP MK Equity', 'JAK MK Equity', 'HSS MK Equity', 'RLEB MK Equity', 'STHB MK Equity', 'SUNVIEW MK Equity',
        'SAMAIDEN MK Equity', 'CITAGLB MK Equity', 'JSB MK Equity', 'MLM MK Equity', 'MNHLDG MK Equity', 'PEKAT MK Equity', 'UZMA MK Equity'
        ]

    dq = MongoConfig.readRAW.find({'ID_BBG': {'$in': ids}, 'DATE': {'$gte': datetime(2022,1,1)}})
    df = pd.DataFrame(dq)
    df.columns = df.columns.str.lower()
    df = df[['date','id_bbg', 'name', 'px_last', 'px_last_1', 'cur_mkt_cap']].copy()
    df.to_csv('green_index_data.csv', index=False)


    repo.index.add([r"green_index_data.csv"])
    repo.git.add(update=True)
    repo.index.commit(COMMIT_MESSAGE)
    origin.push("main")

