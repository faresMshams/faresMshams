from colorama import init, Fore, Style

init(autoreset=True)
BANNER_COLOR = Fore.RED

banner = """
                        ██████╗ ██╗  ██╗ █████╗ ██╗     ██╗    ██╗ █████╗ ███████╗██╗  ██╗
                       ██╔════╝ ██║  ██║██╔══██╗██║     ██║    ██║██╔══██╗██╔════╝██║  ██║
                       ██║  ███╗███████║███████║██║     ██║ █╗ ██║███████║███████╗███████║
                       ██║   ██║██╔══██║██╔══██║██║     ██║███╗██║██╔══██║╚════██║██╔══██║
                       ╚██████╔╝██║  ██║██║  ██║███████╗╚███╔███╔╝██║  ██║███████║██║  ██║
                        ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝ ╚══╝╚══╝ ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝
                                           🚀 Apple Script BY @Mrfa0gh 🚀
"""
for line in banner.splitlines():
    print(f"{BANNER_COLOR}{line}{Style.RESET_ALL}")

print('Script closed ')
input("Press enter key to close ...")
