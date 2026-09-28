# from datetime import date as dt_date, datetime as dt_datetime
# from decimal import Decimal

# import pytest

# from app.models import SpimexTradingResult


# @pytest.fixture()
# def fake_sqlalchemy_full_data() -> list[SpimexTradingResult]:
#     row1 = SpimexTradingResult(
#         id=1,
#         exchange_product_id='A692ALL060J',
#         exchange_product_name=('Бензин (АИ-92-К5), ст. '
#                                'Аллагуват (ст. отправления ОТП)'),
#         oil_id='A692',
#         delivery_basis_id='ALL',
#         delivery_basis_name='ст. Аллагуват',
#         delivery_type_id='J',
#         volume=Decimal('900.00'),
#         total=Decimal('58532400.00'),
#         count=15,
#         date=dt_date(2026, 5, 26),
#         created_on=dt_datetime.fromisoformat(
#             '2026-06-01 05:03:10.171592+03'
#         ),
#         updated_on=dt_datetime.fromisoformat(
#             '2026-06-01 05:03:10.171592+03'
#         )
#     )

#     row2 = SpimexTradingResult(
#         id=2,
#         exchange_product_id='A692ANK060F',
#         exchange_product_name=('Бензин (АИ-92-К5), Ангарск-группа'
#                                ' станций (ст. отправления)'),
#         oil_id='A692',
#         delivery_basis_id='ANK',
#         delivery_basis_name='Ангарск-группа станций',
#         delivery_type_id='F',
#         volume=Decimal('360.00'),
#         total=Decimal('23253840.00'),
#         count=5,
#         date=dt_date(2026, 5, 26),
#         created_on=dt_datetime.fromisoformat(
#             '2026-06-01 05:03:10.171592+03'
#         ),
#         updated_on=dt_datetime.fromisoformat(
#             '2026-06-01 05:03:10.171592+03'
#         )
#     )

#     return [row1, row2]


# @pytest.fixture()
# def fake_sqlalchemy_list_date() -> list[dt_date]:
#     list_date = [
#         dt_date(2026, 5, 27),
#         dt_date(2026, 5, 26),
#         dt_date(2026, 5, 25),
#         dt_date(2026, 5, 22),
#         dt_date(2026, 5, 21),
#         dt_date(2026, 5, 20),
#         dt_date(2026, 5, 19),
#         dt_date(2026, 5, 18),
#     ]
#     return list_date
