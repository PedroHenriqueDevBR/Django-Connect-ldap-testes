from django.http import request
from django.shortcuts import redirect, render
from django.views.generic.base import View


import ldap.modlist as modlist
import ldap
import base64, sys


def get_connection():
    username = 'tony@teste.net'
    password = 'senha'

    conn = ldap.initialize("ldap://0.0.0.0:389") # Conectado através do "telnet 172.16.255.115 389"
    conn.set_option(ldap.OPT_REFERRALS, 0)
    
    conn.simple_bind_s(username, password)
    return conn


class UsuariosView(View):

    def get(self, request):
        conn = get_connection()
        busca = conn.search_s('dc=teste,dc=net', ldap.SCOPE_SUBTREE, '(objectClass=User)')

        usuarios = []
        for dn, entry in busca:
            try:
                usuarios.append({
                    'name': entry['displayName'][0],
                    'username': entry['sAMAccountName'][0],
                    'principal_name': entry['userPrincipalName'][0],
                })
            except:
                continue
        
        return render(request, 'app/listar_usuarios.html', {'usuarios': usuarios})

    def post(self, request):
        # Endpoint para testes
        name = "Tester"
        second_name = "Um"
        fullname = name + " " + second_name
        mail = "{}.{}@teste.net".format(name, second_name)
        company_id = "{}.{}".format(name, second_name)
        password = "senha"

        base_dn = "OU=Users,DC=teste,DC=net"
        user_dn = 'CN=' + name + ' '  + second_name + ',' + base_dn

        modlist = [
            ("objectClass", [b"inetOrgPerson", b"posixAccount", b"shadowAccount"]),
            ("uid", [b"tester01"]),
            ("sn", [b"tester"]),
            ("givenName", [b"Tester"]),
            ("mail", [b"tester.um@teste.net"]),
            ("cn", [b"Tester Um"]),
            ("displayName", [b"Tester Um"]),
            ("gecos", [b"Tester Um"]),
        ]

        conn = get_connection()
        conn.add_s(user_dn, modlist)

        return redirect('listagem_usuarios')

