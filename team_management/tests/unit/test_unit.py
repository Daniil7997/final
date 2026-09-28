# from datetime import date as dt_date

# from fastapi import Request
# import pytest
# from pytest_mock import MockerFixture
# from pydantic import BaseModel

# from app.core.cache.manager import cache_manager
# from app.schemas import (DatesRequest,
#                          ResultsRequest,
#                          DynamycsRequest)
# from app.logic import (get_trading_dates,
#                        get_trading_dynamics,
#                        get_trading_results)


# class TestCacheUnit:

#     @pytest.mark.unit
#     @pytest.mark.asyncio
#     async def test_cache_get(self, mocker: MockerFixture):
#         b_secret = b'my_secret_data'
#         key = 'some_str'

#         mock_get = mocker.patch.object(cache_manager,
#                                        'get_cache_by_key',
#                                        new_callable=mocker.AsyncMock)
#         mock_get.return_value = b_secret
#         result = await cache_manager.get_cache_by_key(key=key)
#         assert result == b_secret
#         mock_get.assert_called_once_with(key=key)

#     @pytest.mark.unit
#     @pytest.mark.asyncio
#     async def test_cache_set(self, mocker: MockerFixture):
#         b_secret = b'my_secret_data'
#         key = 'some_str'
#         expire = 500

#         mock_set = mocker.patch.object(cache_manager,
#                                        'set_cache_by_key',
#                                        new_callable=mocker.AsyncMock)
#         mock_set.return_value = b_secret
#         result = await cache_manager.set_cache_by_key(key=key,
#                                                       value=b_secret,
#                                                       expire=expire)
#         assert result == b_secret
#         mock_set.assert_called_once_with(key=key,
#                                          value=b_secret,
#                                          expire=expire)

#     @pytest.mark.unit
#     @pytest.mark.asyncio
#     async def test_make_cache_key(self):

#         def get_scope(query_params: bytes):
#             scope = {
#                 'type': 'http',
#                 'method': 'GET',
#                 'path': '/api/v1/items',
#                 'headers': [(b'host', b'testserver')],
#                 'query_string': query_params,
#             }
#             return scope

#         # ------------ standard query params ---------
#         params_standard = b'mytestdata=some_str&another_key=secret'
#         scope_standard = get_scope(query_params=params_standard)
#         request_standard = Request(scope=scope_standard)
#         cache_key_standard = cache_manager.make_cache_key(
#             request=request_standard
#             )

#         # ------------ reverse query params ---------
#         params_reverse = b'another_key=secret&mytestdata=some_str'
#         scope_reverse = get_scope(query_params=params_reverse)
#         request_reverse_params = Request(scope=scope_reverse)
#         cache_key_reverse_params = cache_manager.make_cache_key(
#             request=request_reverse_params
#             )

#         assert cache_key_standard == cache_key_reverse_params
#         assert isinstance(cache_key_standard, str)


# class TestGetTradingDates:

#     @pytest.mark.unit
#     @pytest.mark.asyncio
#     async def test_get_trading_dates(self,
#                                      fake_sqlalchemy_list_date,
#                                      mocker: MockerFixture):
#         fake_repo = mocker.AsyncMock()
#         fake_repo.get_dates.return_value = fake_sqlalchemy_list_date
#         last_days = 8
#         request_data = DatesRequest(last_days=last_days)
#         res = await get_trading_dates(repo=fake_repo,
#                                       data=request_data)

#         dates = res.dates
#         assert isinstance(dates, list)
#         assert len(dates) == last_days
#         assert len(dates) == len(set(dates))
#         assert isinstance(dates[0], dt_date)


# class TestGetTradingDynamics:

#     @pytest.mark.unit
#     @pytest.mark.parametrize(
#         'start_date, end_date, oil_id, delivery_type_id, delivery_basis_id',
#         [
#             (dt_date(2026, 5, 10),
#              dt_date(2026, 5, 30),
#              'A692', 'ALL',
#              'ст. Аллагуват'),

#             (dt_date(2026, 5, 10),
#              dt_date(2026, 5, 30),
#              None,
#              None,
#              None)
#             ]
#     )
#     @pytest.mark.asyncio
#     async def test_get_trading_dynamics(self,
#                                         fake_sqlalchemy_full_data,
#                                         mocker: MockerFixture,
#                                         # parameters
#                                         start_date: dt_date,
#                                         end_date: dt_date,
#                                         oil_id: str | None,
#                                         delivery_type_id: str | None,
#                                         delivery_basis_id: str | None):
#         fake_repo = mocker.AsyncMock()
#         fake_repo.get_dynamics.return_value = fake_sqlalchemy_full_data
#         request_data = DynamycsRequest(start_date=start_date,
#                                        end_date=end_date,
#                                        oil_id=oil_id,
#                                        delivery_type_id=delivery_type_id,
#                                        delivery_basis_id=delivery_basis_id)
#         res = await get_trading_dynamics(repo=fake_repo,
#                                          data=request_data)
#         assert isinstance(res, list)
#         assert isinstance(res[0], BaseModel)


# class TestGetTradingResults:

#     @pytest.mark.unit
#     @pytest.mark.parametrize(
#         'oil_id, delivery_type_id, delivery_basis_id, limit',
#         [
#             ('A692', 'ALL', 'ст. Аллагуват', 10),
#             (None, None, None, 20)
#             ]
#     )
#     @pytest.mark.asyncio
#     async def test_get_trading_results(self,
#                                        fake_sqlalchemy_full_data,
#                                        mocker: MockerFixture,
#                                        # parameters
#                                        oil_id: str | None,
#                                        delivery_type_id: str | None,
#                                        delivery_basis_id: str | None,
#                                        limit: int):

#         fake_repo = mocker.AsyncMock()
#         fake_repo.get_results.return_value = fake_sqlalchemy_full_data
#         request_data = ResultsRequest(oil_id=oil_id,
#                                       delivery_type_id=delivery_type_id,
#                                       delivery_basis_id=delivery_basis_id,
#                                       limit=limit)
#         res = await get_trading_results(repo=fake_repo,
#                                         data=request_data)
#         assert isinstance(res, list)
#         assert isinstance(res[0], BaseModel)
