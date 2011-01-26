from string import Template

bash_template = Template("""\
_repoman()
{
    local current previous options commands
    COMPREPLY=()
    current="${COMP_WORDS[COMP_CWORD]}"
    previous="${COMP_WORDS[COMP_CWORD-1]}"
    generic_flags="--help --help-all --version"
    config_flags="--host --port --proxy"
    # Special options
    host_opt="--host"
    port_opt="--port"
    proxy_opt="--proxy"

    subcommands_list="${_SUBCOMMANDS_LIST_}"
    subcommands_array=${_SUBCOMMANDS_ARRAY_}

    subcommand=""
    for cmd in ${subcommands_array[@]}; do
        if [[ "$COMP_LINE" != "${COMP_LINE/$cmd/}" ]]; then
            subcommand=$cmd
            break
        fi
    done

    if [[ ${previous} == ${host_opt} ]]; then
        COMPREPLY=( $(compgen -A hostname ${current}) )
        return 0
    elif [[ ${previous} == ${port_opt} ]]; then
        # do nothing
        return 0
    elif [[ ${previous} == ${proxy_opt} ]]; then
        COMPREPLY=( $(compgen -f ${current}) )
        return 0
    fi

    opts=""

    case $subcommand in
        "")
            opts=$generic_flags;;

        # Case statements from here down were automatically generated
${_CASE_STATEMENTS_}
        # End of automatically generated case statements
    esac


    if [[ ${current} == -* ]]; then
        COMPREPLY=( $(compgen -W "${opts} ${config_flags}" -- ${current}) )
        return 0
    elif [[ ${subcommand} == "" ]]; then
        COMPREPLY=( $(compgen -W "${subcommands_list}" -- ${current}) )
        return 0
    else
        return 0
    fi
}
complete -F _repoman repoman

""")

statement = Template("""\
        "${COMMAND}")
            opts="${OPTIONS}";;

""")



def gen_bash():
    from repoman_client import subcommands
    subcmds = subcommands.subcommands

    cmds = [c.command for c in subcmds]

    keys = {'_SUBCOMMANDS_LIST_':" ".join(cmds),
            '_SUBCOMMANDS_ARRAY_':str(tuple(cmds)).replace(',', ''),
            }

    case_statements = []

    for cmd in subcommands.subcommands:
        cmd = cmd()
        p = cmd.get_parser()
        options = []
        for action in p._actions:
            if action.option_strings:
                options.append(action.option_strings[-1])

        cmd_keys = {'COMMAND':cmd.command,
                    'OPTIONS':" ".join(options)}
        case_statements.append(statement.safe_substitute(cmd_keys))

    keys.update({'_CASE_STATEMENTS_':"".join(case_statements)})

    out_f = open('./repoman_completion', 'w')
    out_f.write(bash_template.safe_substitute(keys))
    out_f.close()

