from fastapi import APIRouter, Depends
from api.schemas import CryptoPricesResponse
from api.auth import current_user
from core.market import get_crypto_prices

router = APIRouter()


@router.get("/market/crypto", response_model=CryptoPricesResponse)
def crypto_prices(user=Depends(current_user)):
    result = get_crypto_prices()
    return CryptoPricesResponse(**result)

# '**' is a python operator used to umpack the dictionary into keyword arguments.
