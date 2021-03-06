# -*- coding: utf-8 -*-

# PLEASE DO NOT EDIT THIS FILE, IT IS GENERATED AND WILL BE OVERWRITTEN:
# https://github.com/ccxt/ccxt/blob/master/CONTRIBUTING.md#how-to-contribute-code

from ccxt.base.exchange import Exchange
from ccxt.base.errors import ExchangeError
from ccxt.base.errors import ArgumentsRequired


class luno(Exchange):

    def describe(self):
        return self.deep_extend(super(luno, self).describe(), {
            'id': 'luno',
            'name': 'luno',
            'countries': ['GB', 'SG', 'ZA'],
            'rateLimit': 1000,
            'version': '1',
            'has': {
                'cancelOrder': True,
                'CORS': False,
                'createOrder': True,
                'fetchAccounts': True,
                'fetchBalance': True,
                'fetchClosedOrders': True,
                'fetchLedger': True,
                'fetchMarkets': True,
                'fetchMyTrades': True,
                'fetchOpenOrders': True,
                'fetchOrder': True,
                'fetchOrderBook': True,
                'fetchOrders': True,
                'fetchTicker': True,
                'fetchTickers': True,
                'fetchTrades': True,
                'fetchTradingFee': True,
                'fetchTradingFees': True,
            },
            'urls': {
                'referral': 'https://www.luno.com/invite/44893A',
                'logo': 'https://user-images.githubusercontent.com/1294454/27766607-8c1a69d8-5ede-11e7-930c-540b5eb9be24.jpg',
                'api': 'https://api.luno.com/api',
                'www': 'https://www.luno.com',
                'doc': [
                    'https://www.luno.com/en/api',
                    'https://npmjs.org/package/bitx',
                    'https://github.com/bausmeier/node-bitx',
                ],
            },
            'api': {
                'public': {
                    'get': [
                        'orderbook',
                        'orderbook_top',
                        'ticker',
                        'tickers',
                        'trades',
                    ],
                },
                'private': {
                    'get': [
                        'accounts/{id}/pending',
                        'accounts/{id}/transactions',
                        'balance',
                        'beneficiaries',
                        'fee_info',
                        'funding_address',
                        'listorders',
                        'listtrades',
                        'orders/{id}',
                        'quotes/{id}',
                        'withdrawals',
                        'withdrawals/{id}',
                    ],
                    'post': [
                        'accounts',
                        'accounts/{id}/name',
                        'postorder',
                        'marketorder',
                        'stoporder',
                        'funding_address',
                        'withdrawals',
                        'send',
                        'quotes',
                        'oauth2/grant',
                    ],
                    'put': [
                        'accounts/{id}/name',
                        'quotes/{id}',
                    ],
                    'delete': [
                        'quotes/{id}',
                        'withdrawals/{id}',
                    ],
                },
            },
        })

    def fetch_markets(self, params={}):
        response = self.publicGetTickers(params)
        result = []
        for i in range(0, len(response['tickers'])):
            market = response['tickers'][i]
            id = market['pair']
            baseId = id[0:3]
            quoteId = id[3:6]
            base = self.safe_currency_code(baseId)
            quote = self.safe_currency_code(quoteId)
            symbol = base + '/' + quote
            result.append({
                'id': id,
                'symbol': symbol,
                'base': base,
                'quote': quote,
                'baseId': baseId,
                'quoteId': quoteId,
                'info': market,
                'active': None,
                'precision': self.precision,
                'limits': self.limits,
            })
        return result

    def fetch_accounts(self, params={}):
        response = self.privateGetBalance(params)
        wallets = self.safe_value(response, 'balance', [])
        result = []
        for i in range(0, len(wallets)):
            account = wallets[i]
            accountId = self.safe_string(account, 'account_id')
            currencyId = self.safe_string(account, 'asset')
            code = self.safe_currency_code(currencyId)
            result.append({
                'id': accountId,
                'type': None,
                'currency': code,
                'info': account,
            })
        return result

    def fetch_balance(self, params={}):
        self.load_markets()
        response = self.privateGetBalance(params)
        wallets = self.safe_value(response, 'balance', [])
        result = {'info': response}
        for i in range(0, len(wallets)):
            wallet = wallets[i]
            currencyId = self.safe_string(wallet, 'asset')
            code = self.safe_currency_code(currencyId)
            reserved = self.safe_float(wallet, 'reserved')
            unconfirmed = self.safe_float(wallet, 'unconfirmed')
            balance = self.safe_float(wallet, 'balance')
            account = self.account()
            account['used'] = self.sum(reserved, unconfirmed)
            account['total'] = self.sum(balance, unconfirmed)
            result[code] = account
        return self.parse_balance(result)

    def fetch_order_book(self, symbol, limit=None, params={}):
        self.load_markets()
        method = 'publicGetOrderbook'
        if limit is not None:
            if limit <= 100:
                method += 'Top'  # get just the top of the orderbook when limit is low
        request = {
            'pair': self.market_id(symbol),
        }
        response = getattr(self, method)(self.extend(request, params))
        timestamp = self.safe_integer(response, 'timestamp')
        return self.parse_order_book(response, timestamp, 'bids', 'asks', 'price', 'volume')

    def parse_order(self, order, market=None):
        #
        #     {
        #         "base": "string",
        #         "completed_timestamp": "string",
        #         "counter": "string",
        #         "creation_timestamp": "string",
        #         "expiration_timestamp": "string",
        #         "fee_base": "string",
        #         "fee_counter": "string",
        #         "limit_price": "string",
        #         "limit_volume": "string",
        #         "order_id": "string",
        #         "pair": "string",
        #         "state": "PENDING",
        #         "type": "BID"
        #     }
        #
        timestamp = self.safe_integer(order, 'creation_timestamp')
        status = 'open' if (order['state'] == 'PENDING') else 'closed'
        side = 'sell' if (order['type'] == 'ASK') else 'buy'
        marketId = self.safe_string(order, 'pair')
        symbol = self.safe_symbol(marketId, market)
        price = self.safe_float(order, 'limit_price')
        amount = self.safe_float(order, 'limit_volume')
        quoteFee = self.safe_float(order, 'fee_counter')
        baseFee = self.safe_float(order, 'fee_base')
        filled = self.safe_float(order, 'base')
        cost = self.safe_float(order, 'counter')
        remaining = None
        if amount is not None:
            if filled is not None:
                remaining = max(0, amount - filled)
        fee = {'currency': None}
        if quoteFee:
            fee['cost'] = quoteFee
            if market is not None:
                fee['currency'] = market['quote']
        else:
            fee['cost'] = baseFee
            if market is not None:
                fee['currency'] = market['base']
        id = self.safe_string(order, 'order_id')
        return {
            'id': id,
            'clientOrderId': None,
            'datetime': self.iso8601(timestamp),
            'timestamp': timestamp,
            'lastTradeTimestamp': None,
            'status': status,
            'symbol': symbol,
            'type': None,
            'side': side,
            'price': price,
            'amount': amount,
            'filled': filled,
            'cost': cost,
            'remaining': remaining,
            'trades': None,
            'fee': fee,
            'info': order,
            'average': None,
        }

    def fetch_order(self, id, symbol=None, params={}):
        self.load_markets()
        request = {
            'id': id,
        }
        response = self.privateGetOrdersId(self.extend(request, params))
        return self.parse_order(response)

    def fetch_orders_by_state(self, state=None, symbol=None, since=None, limit=None, params={}):
        self.load_markets()
        request = {}
        market = None
        if state is not None:
            request['state'] = state
        if symbol is not None:
            market = self.market(symbol)
            request['pair'] = market['id']
        response = self.privateGetListorders(self.extend(request, params))
        orders = self.safe_value(response, 'orders', [])
        return self.parse_orders(orders, market, since, limit)

    def fetch_orders(self, symbol=None, since=None, limit=None, params={}):
        return self.fetch_orders_by_state(None, symbol, since, limit, params)

    def fetch_open_orders(self, symbol=None, since=None, limit=None, params={}):
        return self.fetch_orders_by_state('PENDING', symbol, since, limit, params)

    def fetch_closed_orders(self, symbol=None, since=None, limit=None, params={}):
        return self.fetch_orders_by_state('COMPLETE', symbol, since, limit, params)

    def parse_ticker(self, ticker, market=None):
        timestamp = self.safe_integer(ticker, 'timestamp')
        symbol = None
        if market:
            symbol = market['symbol']
        last = self.safe_float(ticker, 'last_trade')
        return {
            'symbol': symbol,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'high': None,
            'low': None,
            'bid': self.safe_float(ticker, 'bid'),
            'bidVolume': None,
            'ask': self.safe_float(ticker, 'ask'),
            'askVolume': None,
            'vwap': None,
            'open': None,
            'close': last,
            'last': last,
            'previousClose': None,
            'change': None,
            'percentage': None,
            'average': None,
            'baseVolume': self.safe_float(ticker, 'rolling_24_hour_volume'),
            'quoteVolume': None,
            'info': ticker,
        }

    def fetch_tickers(self, symbols=None, params={}):
        self.load_markets()
        response = self.publicGetTickers(params)
        tickers = self.index_by(response['tickers'], 'pair')
        ids = list(tickers.keys())
        result = {}
        for i in range(0, len(ids)):
            id = ids[i]
            market = self.safe_market(id)
            symbol = market['symbol']
            ticker = tickers[id]
            result[symbol] = self.parse_ticker(ticker, market)
        return self.filter_by_array(result, 'symbol', symbols)

    def fetch_ticker(self, symbol, params={}):
        self.load_markets()
        market = self.market(symbol)
        request = {
            'pair': market['id'],
        }
        response = self.publicGetTicker(self.extend(request, params))
        return self.parse_ticker(response, market)

    def parse_trade(self, trade, market):
        # For public trade data(is_buy is True) indicates 'buy' side but for private trade data
        # is_buy indicates maker or taker. The value of "type"(ASK/BID) indicate sell/buy side.
        # Private trade data includes ID field which public trade data does not.
        orderId = self.safe_string(trade, 'order_id')
        takerOrMaker = None
        side = None
        if orderId is not None:
            side = 'sell' if (trade['type'] == 'ASK') else 'buy'
            if side == 'sell' and trade['is_buy']:
                takerOrMaker = 'maker'
            elif side == 'buy' and not trade['is_buy']:
                takerOrMaker = 'maker'
            else:
                takerOrMaker = 'taker'
        else:
            side = 'buy' if trade['is_buy'] else 'sell'
        feeBase = self.safe_float(trade, 'fee_base')
        feeCounter = self.safe_float(trade, 'fee_counter')
        feeCurrency = None
        feeCost = None
        if feeBase is not None:
            if feeBase != 0.0:
                feeCurrency = market['base']
                feeCost = feeBase
        elif feeCounter is not None:
            if feeCounter != 0.0:
                feeCurrency = market['quote']
                feeCost = feeCounter
        timestamp = self.safe_integer(trade, 'timestamp')
        return {
            'info': trade,
            'id': None,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'symbol': market['symbol'],
            'order': orderId,
            'type': None,
            'side': side,
            'takerOrMaker': takerOrMaker,
            'price': self.safe_float(trade, 'price'),
            'amount': self.safe_float(trade, 'volume'),
            # Does not include potential fee costs
            'cost': self.safe_float(trade, 'counter'),
            'fee': {
                'cost': feeCost,
                'currency': feeCurrency,
            },
        }

    def fetch_trades(self, symbol, since=None, limit=None, params={}):
        self.load_markets()
        market = self.market(symbol)
        request = {
            'pair': market['id'],
        }
        if since is not None:
            request['since'] = since
        response = self.publicGetTrades(self.extend(request, params))
        trades = self.safe_value(response, 'trades', [])
        return self.parse_trades(trades, market, since, limit)

    def fetch_my_trades(self, symbol=None, since=None, limit=None, params={}):
        if symbol is None:
            raise ArgumentsRequired(self.id + ' fetchMyTrades requires a symbol argument')
        self.load_markets()
        market = self.market(symbol)
        request = {
            'pair': market['id'],
        }
        if since is not None:
            request['since'] = since
        if limit is not None:
            request['limit'] = limit
        response = self.privateGetListtrades(self.extend(request, params))
        trades = self.safe_value(response, 'trades', [])
        return self.parse_trades(trades, market, since, limit)

    def fetch_trading_fees(self, params={}):
        self.load_markets()
        response = self.privateGetFeeInfo(params)
        return {
            'info': response,
            'maker': self.safe_float(response, 'maker_fee'),
            'taker': self.safe_float(response, 'taker_fee'),
        }

    def create_order(self, symbol, type, side, amount, price=None, params={}):
        self.load_markets()
        method = 'privatePost'
        request = {
            'pair': self.market_id(symbol),
        }
        if type == 'market':
            method += 'Marketorder'
            request['type'] = side.upper()
            if side == 'buy':
                request['counter_volume'] = amount
            else:
                request['base_volume'] = amount
        else:
            method += 'Postorder'
            request['volume'] = amount
            request['price'] = price
            request['type'] = 'BID' if (side == 'buy') else 'ASK'
        response = getattr(self, method)(self.extend(request, params))
        return {
            'info': response,
            'id': response['order_id'],
        }

    def cancel_order(self, id, symbol=None, params={}):
        self.load_markets()
        request = {
            'order_id': id,
        }
        return self.privatePostStoporder(self.extend(request, params))

    def fetch_ledger_by_entries(self, code=None, entry=-1, limit=1, params={}):
        # by default without entry number or limit number, return most recent entry
        since = None
        request = {
            'min_row': entry,
            'max_row': self.sum(entry, limit),
        }
        return self.fetch_ledger(code, since, limit, self.extend(request, params))

    def fetch_ledger(self, code=None, since=None, limit=None, params={}):
        self.load_markets()
        self.load_accounts()
        currency = None
        id = self.safe_string(params, 'id')  # account id
        min_row = self.safe_value(params, 'min_row')
        max_row = self.safe_value(params, 'max_row')
        if id is None:
            if code is None:
                raise ArgumentsRequired(self.id + ' fetchLedger() requires a currency code argument if no account id specified in params')
            currency = self.currency(code)
            accountsByCurrencyCode = self.index_by(self.accounts, 'currency')
            account = self.safe_value(accountsByCurrencyCode, code)
            if account is None:
                raise ExchangeError(self.id + ' fetchLedger() could not find account id for ' + code)
            id = account['id']
        if min_row is None and max_row is None:
            max_row = 0  # Default to most recent transactions
            min_row = -1000  # Maximum number of records supported
        elif min_row is None or max_row is None:
            raise ExchangeError(self.id + " fetchLedger() require both params 'max_row' and 'min_row' or neither to be defined")
        if limit is not None and max_row - min_row > limit:
            if max_row <= 0:
                min_row = max_row - limit
            elif min_row > 0:
                max_row = min_row + limit
        if max_row - min_row > 1000:
            raise ExchangeError(self.id + " fetchLedger() requires the params 'max_row' - 'min_row' <= 1000")
        request = {
            'id': id,
            'min_row': min_row,
            'max_row': max_row,
        }
        response = self.privateGetAccountsIdTransactions(self.extend(params, request))
        entries = self.safe_value(response, 'transactions', [])
        return self.parse_ledger(entries, currency, since, limit)

    def parse_ledger_comment(self, comment):
        words = comment.split(' ')
        types = {
            'Withdrawal': 'fee',
            'Trading': 'fee',
            'Payment': 'transaction',
            'Sent': 'transaction',
            'Deposit': 'transaction',
            'Received': 'transaction',
            'Released': 'released',
            'Reserved': 'reserved',
            'Sold': 'trade',
            'Bought': 'trade',
            'Failure': 'failed',
        }
        referenceId = None
        firstWord = self.safe_string(words, 0)
        thirdWord = self.safe_string(words, 2)
        fourthWord = self.safe_string(words, 3)
        type = self.safe_string(types, firstWord, None)
        if (type is None) and (thirdWord == 'fee'):
            type = 'fee'
        if (type == 'reserved') and (fourthWord == 'order'):
            referenceId = self.safe_string(words, 4)
        return {
            'type': type,
            'referenceId': referenceId,
        }

    def parse_ledger_entry(self, entry, currency=None):
        # details = self.safe_value(entry, 'details', {})
        id = self.safe_string(entry, 'row_index')
        account_id = self.safe_string(entry, 'account_id')
        timestamp = self.safe_value(entry, 'timestamp')
        currencyId = self.safe_string(entry, 'currency')
        code = self.safe_currency_code(currencyId, currency)
        available_delta = self.safe_float(entry, 'available_delta')
        balance_delta = self.safe_float(entry, 'balance_delta')
        after = self.safe_float(entry, 'balance')
        comment = self.safe_string(entry, 'description')
        before = after
        amount = 0.0
        result = self.parse_ledger_comment(comment)
        type = result['type']
        referenceId = result['referenceId']
        direction = None
        status = None
        if balance_delta != 0.0:
            before = after - balance_delta  # TODO: float precision
            status = 'ok'
            amount = abs(balance_delta)
        elif available_delta < 0.0:
            status = 'pending'
            amount = abs(available_delta)
        elif available_delta > 0.0:
            status = 'canceled'
            amount = abs(available_delta)
        if balance_delta > 0 or available_delta > 0:
            direction = 'in'
        elif balance_delta < 0 or available_delta < 0:
            direction = 'out'
        return {
            'id': id,
            'direction': direction,
            'account': account_id,
            'referenceId': referenceId,
            'referenceAccount': None,
            'type': type,
            'currency': code,
            'amount': amount,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'before': before,
            'after': after,
            'status': status,
            'fee': None,
            'info': entry,
        }

    def sign(self, path, api='public', method='GET', params={}, headers=None, body=None):
        url = self.urls['api'] + '/' + self.version + '/' + self.implode_params(path, params)
        query = self.omit(params, self.extract_params(path))
        if query:
            url += '?' + self.urlencode(query)
        if api == 'private':
            self.check_required_credentials()
            auth = self.string_to_base64(self.apiKey + ':' + self.secret)
            headers = {
                'Authorization': 'Basic ' + self.decode(auth),
            }
        return {'url': url, 'method': method, 'body': body, 'headers': headers}

    def request(self, path, api='public', method='GET', params={}, headers=None, body=None):
        response = self.fetch2(path, api, method, params, headers, body)
        if 'error' in response:
            raise ExchangeError(self.id + ' ' + self.json(response))
        return response
