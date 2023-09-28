




 

def pw_encryption(pw_dir="./.store"):

    from cryptography.fernet import Fernet
    import getpass

    ### 1. give a name for the system which you are saving the password for
    try:
        system_name = input("Please provide system description: ")
    except Exception as error:
        print('ERROR', error)
    else:
        print('System name provided: ', system_name)

    ### 2. enter the password
    try:
        pw = getpass.getpass()
    except Exception as error:
        print('ERROR', error)
    else:
        print('Password entered: ', "*"*len(pw))

    ### 3. generate key and write it in a file
    key = Fernet.generate_key()
    f = open(pw_dir + "/" + system_name + "_" + "refKey.encr", "wb")
    f.write(key)
    f.close()

    ### 3. encrypt the password and write it in a file
    refKey = Fernet(key)
    pwbyt = bytes(pw, 'utf-8') # convert into byte
    encryptedPWD = refKey.encrypt(pwbyt)
    f = open(pw_dir + "/" + system_name + "_" + "encryptedPWD.encr", "wb")
    f.write(encryptedPWD)
    f.close()



def pw_decrypt(system_name, pw_dir="./.store"):
    
    from cryptography.fernet import Fernet

    with open(pw_dir + "/" + system_name + "_" + "encryptedPWD.encr") as f:
        encpw = ''.join(f.readlines())
        encpwbyt = bytes(encpw, 'utf-8')
    f.close()

    # read key and convert into byte
    with open(pw_dir + "/" + system_name + "_" + "refKey.encr") as f:
        refKey = ''.join(f.readlines())
        refKeybyt = bytes(refKey, 'utf-8')
    f.close()

    # use the key and encrypt pwd
    keytouse = Fernet(refKeybyt)
    myPass = (keytouse.decrypt(encpwbyt))
    return myPass.decode('utf-8')

