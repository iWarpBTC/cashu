import asyncio

from environs import Env
from fastapi import APIRouter

from lnbits.db import Database
from lnbits.helpers import template_renderer
from lnbits.tasks import catch_everything_and_restart

db = Database("ext_cashu")


cashu_static_files = [
    {
        "path": "/cashu/static",
        "name": "cashu_static",
    }
]
from .lib.cashu.lightning.base import Wallet
from .lib.cashu.mint.ledger import Ledger

env = Env()
env.read_env()

ledger = Ledger(
    db=db,  # type: ignore
    seed=env.str("CASHU_PRIVATE_KEY", default="SuperSecretPrivateKey"),
    derivation_path="0/0/0/1",
    lightning=Wallet,  # type: ignore
)

cashu_ext: APIRouter = APIRouter(prefix="/cashu", tags=["cashu"])


def cashu_renderer():
    return template_renderer(["cashu/templates"])


from .tasks import startup_cashu_mint, wait_for_paid_invoices
from .views import *  # noqa: F401,F403
from .views_api import *  # noqa: F401,F403


def cashu_start():
    loop = asyncio.get_event_loop()
    loop.create_task(catch_everything_and_restart(startup_cashu_mint))
    loop.create_task(catch_everything_and_restart(wait_for_paid_invoices))
