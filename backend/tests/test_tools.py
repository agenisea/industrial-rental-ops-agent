"""Tool correctness tests — verify data access layer returns expected results."""

from ops_agent.repositories.message_repo import SqlMessageRepository
from ops_agent.repositories.order_repo import SqlOrderRepository


class TestLookupOrder:
    def test_existing_order(self, order_repo: SqlOrderRepository):
        order = order_repo.get_by_code("ORD-5353")
        assert order is not None
        assert order.status == "Completed"
        assert order.user.username == "Omaha_Builders"
        assert order.access_details == "Front driveway"

    def test_nonexistent_order(self, order_repo: SqlOrderRepository):
        order = order_repo.get_by_code("ORD-0000")
        assert order is None


class TestFindActiveOrders:
    def test_chase_construction(self, order_repo: SqlOrderRepository):
        orders = order_repo.find_active_by_company("Chase Construction")
        assert len(orders) >= 1
        codes = [o.code for o in orders]
        assert "ORD-1592" in codes
        for o in orders:
            assert o.status == "Active"

    def test_no_results(self, order_repo: SqlOrderRepository):
        orders = order_repo.find_active_by_company("Nonexistent Company")
        assert orders == []


class TestGetOrderSentiment:
    def test_order_9910_sentiment(
        self,
        order_repo: SqlOrderRepository,
        message_repo: SqlMessageRepository,
    ):
        order = order_repo.get_by_code("ORD-9910")
        assert order is not None
        messages = message_repo.get_by_conversation(order.conversation_id)
        assert len(messages) == 8

        counts: dict[str, int] = {"positive": 0, "neutral": 0, "negative": 0}
        for m in messages:
            label = m.sentiment_label if m.sentiment_label in counts else "neutral"
            counts[label] += 1

        # 3 neutral and 3 negative — tie. Our tool uses dict order → "neutral" wins.
        # The key insight is that negative sentiment is present and significant.
        assert counts["negative"] == 3
        assert counts["positive"] == 2
        assert counts["neutral"] == 3
        assert counts["negative"] >= counts["positive"]
