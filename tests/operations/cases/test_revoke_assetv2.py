from unittest.mock import patch

from django.conf import settings


def test_revoke_assetv2(connector_config):
    settings.configure()
    from connector_sekoia_io_xdr.operations.cases.revoke_assetv2 import revoke_assetv2

    with patch("connector_sekoia_io_xdr.utils.GenericAPIAction.run") as query:
        query.return_value = {
            "uuid": "82aa4cea-41fd-4381-8bb9-7100e7f97460",
            "revoked": True,
        }

        result = revoke_assetv2(
            config=connector_config,
            params={"uuid": "82aa4cea-41fd-4381-8bb9-7100e7f97460"},
        )

        assert result is not None
        assert result["uuid"] == "82aa4cea-41fd-4381-8bb9-7100e7f97460"
        assert result["revoked"] is True
