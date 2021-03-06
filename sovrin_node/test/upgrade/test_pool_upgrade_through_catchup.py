import pytest
from copy import deepcopy

from stp_core.loop.eventually import eventually
from plenum.common.constants import VERSION, NAME
from plenum.common.util import randomString
from plenum.test.test_node import checkNodesConnected
from sovrin_common.constants import SHA256, CANCEL, ACTION
from sovrin_node.test.conftest import tconf, testNodeClass, testClientClass
from plenum.test.conftest import allPluginsPath
from sovrin_node.test.helper import TestNode
from sovrin_node.test.upgrade.helper import bumpVersion, sendUpgrade, \
    ensureUpgradeSent, checkUpgradeScheduled


whitelist = ['Failed to upgrade node']


@pytest.fixture(scope="module")
def txnPoolNodeSet(tconf, nodeSet):
    for node in nodeSet:
        node.config = tconf
        node.upgrader.config = tconf
    return nodeSet


@pytest.mark.skip(reason='SOV-559. Failing on Windows')
def testUpgradeLatestUncancelledVersion(looper,
                                        txnPoolNodeSet, tconf, nodeThetaAdded,
                                        validUpgrade, trustee, trusteeWallet,
                                        tdirWithPoolTxns, allPluginsPath):
    """
    A node starts and finds several upgrades but selects the latest one which
    is not cancelled, eg node is on version 1.2 but finds 1.3, 1.4 and 1.5 but
    since 1.5 is cancelled, it selects 1.4
    """
    nodeSet = txnPoolNodeSet
    newSteward, newStewardWallet, newNode = nodeThetaAdded
    for node in nodeSet[:-1]:
        node.nodestack.removeRemoteByName(newNode.nodestack.name)
        newNode.nodestack.removeRemoteByName(node.nodestack.name)
    newNode.stop()
    nodeSet = nodeSet[:-1]
    looper.removeProdable(newNode)

    upgr1 = deepcopy(validUpgrade)

    upgr2 = deepcopy(upgr1)
    upgr2[VERSION] = bumpVersion(upgr1[VERSION])
    upgr2[NAME] += randomString(3)
    upgr2[SHA256] = randomString(32)

    upgr3 = deepcopy(upgr2)
    upgr3[VERSION] = bumpVersion(upgr2[VERSION])
    upgr3[NAME] += randomString(3)
    upgr3[SHA256] = randomString(32)

    upgr4 = deepcopy(upgr3)
    upgr4[ACTION] = CANCEL

    ensureUpgradeSent(looper, trustee, trusteeWallet, upgr1)
    looper.run(eventually(checkUpgradeScheduled, nodeSet[:-1], upgr1[VERSION],
                          retryWait=1, timeout=5))

    ensureUpgradeSent(looper, trustee, trusteeWallet, upgr2)
    looper.run(eventually(checkUpgradeScheduled, nodeSet[:-1], upgr2[VERSION],
                          retryWait=1, timeout=5))

    ensureUpgradeSent(looper, trustee, trusteeWallet, upgr3)
    looper.run(eventually(checkUpgradeScheduled, nodeSet[:-1], upgr3[VERSION],
                          retryWait=1, timeout=5))

    ensureUpgradeSent(looper, trustee, trusteeWallet, upgr4)
    looper.run(eventually(checkUpgradeScheduled, nodeSet[:-1], upgr2[VERSION],
                          retryWait=1, timeout=5))

    trustee.stopRetrying()

    newNode = TestNode(newNode.name, basedirpath=tdirWithPoolTxns,
                       config=tconf, pluginPaths=allPluginsPath,
                       ha=newNode.nodestack.ha, cliha=newNode.clientstack.ha)
    looper.add(newNode)
    nodeSet.append(newNode)
    looper.run(checkNodesConnected(nodeSet, overrideTimeout=30))

    looper.run(eventually(checkUpgradeScheduled, [newNode, ], upgr2[VERSION],
                          retryWait=1, timeout=10))


