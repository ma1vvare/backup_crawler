# separator used by search.py, categories.py, ...
SEPARATOR = ";"

LANG            = "zh_TW" # can be en_US, fr_FR, ...
ANDROID_ID      = "1AF516EFACD646F" # "xxxxxxxxxxxxxxxx"
GOOGLE_LOGIN    = "s22928868@gmail.com" # "username@gmail.com"
GOOGLE_PASSWORD = "22928868"
# GOOGLE_LOGIN    = "testbotsong@gmail.com"
# GOOGLE_PASSWORD = "1qaz!@#$"
AUTH_TOKEN      = None # "yyyyyyyyy"

# force the user to edit this file
if any([each == None for each in [ANDROID_ID, GOOGLE_LOGIN, GOOGLE_PASSWORD]]):
    raise Exception("config.py not updated")

locale_timestring = {
    'en_US':'%b %d, %Y',
    'zh_TW':'%Y\345\271\264%m\346\234\210%d\346\227\245',
    'ja_JP':'%Y\345\271\264%m\346\234\210%d\346\227\245'
}
dangerous_permission = ["android.permission.READ_CALENDAR",
                                "android.permission.WRITE_CALENDAR",
                                "android.permission.CAMERA",
                                "android.permission.READ_CONTACTS",
                                "android.permission.WRITE_CONTACTS",
                                "android.permission.GET_ACCOUNTS",
                                "android.permission.ACCESS_FINE_LOCATION",
                                "android.permission.ACCESS_COARSE_LOCATION",
                                "android.permission.RECORD_AUDIO",
                                "android.permission.READ_PHONE_STATE",
                                "android.permission.CALL_PHONE",
                                "android.permission.READ_CALL_LOG",
                                "android.permission.WRITE_CALL_LOG",
                                "android.permission.ADD_VOICEMAIL",
                                "android.permission.USE_SIP",
                                "android.permission.PROCESS_OUTGOING_CALLS",
                                "android.permission.BODY_SENSORS",
                                "android.permission.SEND_SMS",
                                "android.permission.RECEIVE_SMS",
                                "android.permission.READ_SMS",
                                "android.permission.RECEIVE_WAP_PUSH",
                                "android.permission.RECEIVE_MMS",
                                "android.permission.READ_EXTERNAL_STORAGE",
                                "android.permission.WRITE_EXTERNAL_STORAGE"]

api_key =[
'51d63dc8b2860fbd889ea73d564e361e1ec795ce2daadb1046771272336cdadf',
'20f0728b711931ef2f60c8c403e83c20b600a902a12293a7d1fe566f85ca22dd',
'7ec895bab30a273bf6df3e211105f5f2ee45a96ddea57f53d6e4fe2b98f0c7c1',
'd0fe387a075ca62d0336485641912f1b318240f6132c576fa96dbf81b242da71',
'29b45a9dc40737a7bc894cbacc3da603044e7f3a2651606dfca89de9accab80a',
'51d63dc8b2860fbd889ea73d564e361e1ec795ce2daadb1046771272336cdadf',
'60473b7caf108d05a5f51b9fd7544f6bb7bd0a4d966ca58d0c7b65e43611abc9',
'860011e025932bd8ad550e3174b75ee1c686134543a4635a4e37fef038c0fbec',
'83ddc4aa67adf20cdf89e627741948af3f0e25389586735b814b17e337ff12c6',
'15c419057582671da62b665a8b3ecdfd0ea6a611de7769b87923cf56f87c2e8b',
'1c4e7ac7de87088e9868ea2e90cf1337496c68da534edb6fc65aea779e1bbfe8',
'1afe6660b059b9b57b478a8f5907247b79b44c17c37a9765e5d5dc4679f6d02c',
'3fc2d2e6341017a2c52436aafddc9be6d8ecd16613bbe93395a17cb0b0f13f2b',
'359a1c2e68bc2efd781d92a82a93f15a30e8f3c7b0be8f0ef91871a3021b7041',
'd0b6b469a735ecae24c72671f589ff189d7d28a12c72ab9a594de201a17ab8a8',
'02991544cb99408a0a88a1c860e6cd431c73f7b9af22629486ea668cf7eaafa7',
'cf7b676d76d89421cba98f18e72723305a97226edf3c36731c8d32735193816f',
'90ba473b1276363373150cb6430fedba3889397ef5c59164ede1e8729cb180f9']

api_key_IP = [
'a1e947098140c9de8d20a1a467795d56b92fe14264358e5b5114fc73848ac934',
'5b70e9e00c8596059a9fc6ac0300d00e3044fd5578047f0da455d19057bafe4c',
'02991544cb99408a0a88a1c860e6cd431c73f7b9af22629486ea668cf7eaafa7',
'cf7b676d76d89421cba98f18e72723305a97226edf3c36731c8d32735193816f',
'90ba473b1276363373150cb6430fedba3889397ef5c59164ede1e8729cb180f9']
