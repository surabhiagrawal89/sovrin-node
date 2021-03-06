"""
Full verkey tests
    Add a nym (16 byte, base58) with a full verkey (32 byte, base58) (Form 1)
        { type: NYM, dest: <id2>, verkey: <32byte key> }
    Retrieve the verkey.
        { type: GET_NYM, dest: <id2> }
    Verify a signature from this identifier
    Change a verkey for a nym with a full verkey.
        { type: NYM, dest: <id2>, verkey: <32byte ED25519 key> }
    Retrieve new verkey
        { type: GET_NYM, dest: <id2> }
    Verify a signature from this identifier with the new verkey
"""
from stp_core.loop.eventually import eventually
from plenum.common.signer_did import DidSigner

from sovrin_common.identity import Identity
from sovrin_node.test.did.conftest import pf
from sovrin_node.test.did.helper import chkVerifyForRetrievedIdentity, \
    updateSovrinIdrWithFullKey, \
    fetchFullVerkeyFromSovrin, checkFullVerkeySize, \
    updateWalletIdrWithFullVerkeySigner
from sovrin_client.test.helper import createNym


@pf
def didAddedWithFullVerkey(addedTrustAnchor, looper, trustAnchor, trustAnchorWallet,
                          wallet, fullKeyIdr):
    """{ type: NYM, dest: <id1> }"""
    createNym(looper, fullKeyIdr, trustAnchor, trustAnchorWallet,
              verkey=wallet.getVerkey(fullKeyIdr))
    return wallet


@pf
def newFullKeySigner(wallet, fullKeyIdr):
    return DidSigner(identifier=fullKeyIdr)


@pf
def newFullKey(newFullKeySigner):
    return newFullKeySigner.verkey

@pf
def didUpdatedWithFullVerkey(didAddedWithFullVerkey, looper, trustAnchor,
                            trustAnchorWallet, fullKeyIdr, newFullKey,
                             newFullKeySigner, wallet, client):
    """{ type: NYM, dest: <id1>, verkey: <vk1> }"""
    # updateSovrinIdrWithFullKey(looper, trustAnchorWallet, trustAnchor, wallet,
    #                            fullKeyIdr, newFullKey)
    updateSovrinIdrWithFullKey(looper, wallet, client, wallet,
                               fullKeyIdr, newFullKey)
    updateWalletIdrWithFullVerkeySigner(wallet, fullKeyIdr, newFullKeySigner)


@pf
def newVerkeyFetched(didAddedWithFullVerkey, looper, trustAnchor, trustAnchorWallet,
                     fullKeyIdr, wallet):
    """{ type: GET_NYM, dest: <id1> }"""
    fetchFullVerkeyFromSovrin(looper, trustAnchorWallet, trustAnchor, wallet,
                              fullKeyIdr)


def testAddDidWithVerkey(didAddedWithFullVerkey):
    pass


def testRetrieveFullVerkey(didAddedWithFullVerkey, looper, trustAnchor,
                            trustAnchorWallet, wallet, fullKeyIdr):
    """{ type: GET_NYM, dest: <id1> }"""
    identity = Identity(identifier=fullKeyIdr)
    req = trustAnchorWallet.requestIdentity(identity,
                                        sender=trustAnchorWallet.defaultId)
    trustAnchor.submitReqs(req)

    def chk():
        retrievedVerkey = trustAnchorWallet.getIdentity(fullKeyIdr).verkey
        assert retrievedVerkey == wallet.getVerkey(fullKeyIdr)
        checkFullVerkeySize(retrievedVerkey)

    looper.run(eventually(chk, retryWait=1, timeout=5))
    chkVerifyForRetrievedIdentity(wallet, trustAnchorWallet, fullKeyIdr)


def testChangeVerkeyToNewVerkey(didUpdatedWithFullVerkey):
    pass


def testRetrieveChangedVerkey(didUpdatedWithFullVerkey, newVerkeyFetched):
    pass


def testVerifySigWithChangedVerkey(didUpdatedWithFullVerkey, newVerkeyFetched,
                                   trustAnchorWallet, fullKeyIdr, wallet):
    chkVerifyForRetrievedIdentity(wallet, trustAnchorWallet, fullKeyIdr)
