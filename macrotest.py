from AppOpener import open, close

def main():
    print()
    print("1. Open <any_name> TO OPEN APPLICATIONS")
    print("2. Close <any_name> TO CLOSE APPLICATIONS")
    print()
    open("help")
    print("TRY 'OPEN <any_key>'")
    while True:
        inp = input("ENTER APPLICATION TO OPEN / CLOSE: ").lower()
        if "close " in inp:
            app_name = inp.replace("close ","").strip()
            close(app_name, match_closest=True, output=False) # App will be close be it matches little bit too (Without printing context (like CLOSING <app_name>))
        elif "open " in inp:
            app_name = inp.replace("open ","")
            open(app_name, match_closest=True) # App will be open be it matches little bit too
        
        else:
            app_name = inp
            open(app_name, match_closest=True)
            
if __name__ == '__main__':
    main()
