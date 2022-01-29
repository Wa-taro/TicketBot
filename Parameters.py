# -*- coding: utf-8 -*-

import dataclasses
import datetime


@dataclasses.dataclass
class Parameters:
    userFile: str = dataclasses.field(init=False)
    urlLogin: str = dataclasses.field(init=False)
    # ログイン開始時間
    loginTime: datetime = dataclasses.field(init=False)
    # ログインユーザーのID
    loginUser: str = dataclasses.field(init=False)
    # ログインユーザーのパスワード
    loginPassword: str = dataclasses.field(init=False)
    # 対象チケットのURL
    urlTicket: str = dataclasses.field(init=False)
    # 対象チケットのid属性
    ticketId: str = dataclasses.field(init=False)
    # 枚数選択
    ticketNum: str = dataclasses.field(init=False)
    # チケット受付開始時間
    startTime: datetime = dataclasses.field(init=False)
    # ディレイ秒(時間が来た瞬間にリクエストを送ると弾かれる？)
    delay: float = dataclasses.field(init=False)
