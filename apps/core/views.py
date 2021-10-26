from django.http import request
from django.shortcuts import redirect, render
from django.views.generic.base import View
from django.contrib import messages


import ldap.modlist as modlist
import ldap


def get_connection():
    username = 'username@teste.net'
    password = 'senha123'

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
                    'name': entry['displayName'][0].decode(),
                    'username': entry['sAMAccountName'][0].decode(),
                    'principal_name': entry['userPrincipalName'][0].decode(),
                })
            except:
                continue
        
        return render(request, 'app/listar_usuarios.html', {'usuarios': usuarios})

    def post(self, request):
        # Endpoint para testes
        primeiro_nome = request.POST.get('primeiro_nome')
        ultimo_nome = request.POST.get('ultimo_nome')

        if len(primeiro_nome) == 0 or len(ultimo_nome) == 0:
            messages.add_message(request, messages.INFO, 'Informe o primeiro e o ultimo nome')
            return redirect('listagem_usuarios') 

        nome_completo = primeiro_nome + " " + ultimo_nome
        email = "{}.{}@teste.net".format(primeiro_nome, ultimo_nome)
        company_id = "{}.{}".format(primeiro_nome, ultimo_nome)

        base_dn = "OU=teste,DC=teste,DC=net"
        user_dn = 'CN=' + nome_completo + ',' + base_dn

        modlist = [
            ("objectClass", [b"User", b"posixAccount", b"shadowAccount"]),
            ("cn", [bytes(nome_completo, encoding='utf8')]),
            ("uid", [bytes(company_id, encoding='utf8')]),
            ("userPrincipalName", [bytes(company_id, encoding='utf8')]),
            ("sAMAccountName", [bytes(company_id, encoding='utf8')]),
            ("givenName", [bytes(primeiro_nome, encoding='utf8')]),
            ("sn", [bytes(ultimo_nome, encoding='utf8')]),
            ("mail", [bytes(email, encoding='utf8')]),
            ("displayName", [bytes(nome_completo, encoding='utf8')]),
            ("gecos", [bytes(nome_completo, encoding='utf8')]),
            # ("userAccountControl", [bytes('512', encoding='utf8')]), # Regra que define o usuario como desbloqueado (Impedida pelo Active Directory)
        ]

        conn = get_connection()
        conn.add_s(user_dn, modlist)
        # atualizar Password
        # mod_list = [(ldap.MOD_REPLACE, 'unicodePwd', ['teste123'])] # Tentativa de modificar a senha (Impedida pela politica de segurança do Active Directory)
        # conn.modify_s(user_dn, mod_list)

        return redirect('listagem_usuarios')

