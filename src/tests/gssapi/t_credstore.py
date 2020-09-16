from k5test import *

realm = K5Realm()

mark('gss_store_cred_into() and ccache/keytab')
storagecache = 'FILE:' + os.path.join(realm.testdir, 'user_store')
servicekeytab = os.path.join(realm.testdir, 'kt')
service_cs = 'service/cs@%s' % realm.realm
realm.addprinc(service_cs)
realm.extract_keytab(service_cs, servicekeytab)
realm.kinit(service_cs, None, ['-k', '-t', servicekeytab])
msgs = ('Storing %s -> %s in %s' % (service_cs, realm.krbtgt_princ,
                                    storagecache),
        'Retrieving %s from FILE:%s' % (service_cs, servicekeytab))
realm.run(['./t_credstore', '-s', 'p:' + service_cs, 'ccache', storagecache,
           'keytab', servicekeytab], expected_trace=msgs)

mark('rcache')
# t_credstore -r should produce a replay error normally, but not with
# rcache set to "none:".
output = realm.run(['./t_credstore', '-r', '-a', 'p:' + realm.host_princ],
                   expected_code=1)
if 'gss_accept_sec_context(2): Request is a replay' not in output:
    fail('Expected replay error not seen in t_credstore output')
realm.run(['./t_credstore', '-r', '-a', 'p:' + realm.host_princ,
           'rcache', 'none:'])

# Test password feature.
mark('password')
# Must be used with a desired name.
realm.run(['./t_credstore', '-i', '', 'password', 'pw'],
          expected_code=1, expected_msg='An invalid name was supplied')
# Must not be used with a client keytab.
realm.run(['./t_credstore', '-i', 'u:' + realm.user_princ,
           'password', 'pw', 'client_keytab', servicekeytab],
          expected_code=1, expected_msg='Credential usage type is unknown')
# Must not be used with a ccache.
realm.run(['./t_credstore', '-i', 'u:' + realm.user_princ,
           'password', 'pw', 'ccache', storagecache],
          expected_code=1, expected_msg='Credential usage type is unknown')
# Must be acquiring initiator credentials.
realm.run(['./t_credstore', '-a', 'u:' + realm.user_princ, 'password', 'pw'],
          expected_code=1, expected_msg='Credential usage type is unknown')
msgs = ('Getting initial credentials for %s' % realm.user_princ,
        'Storing %s -> %s in MEMORY:' % (realm.user_princ, realm.krbtgt_princ),
        'Destroying ccache MEMORY:')
realm.run(['./t_credstore', '-i', 'u:' + realm.user_princ, 'password',
           password('user')], expected_trace=msgs)

success('Credential store tests')
