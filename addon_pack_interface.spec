# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['addon_pack_interface.py'],
             pathex=['C:\\Users\\jedel\\PycharmProjects\\jedel_name_generator'],
             binaries=[],
             datas=[('name_data/names_merged_test.db', 'name_data/names_merged_test.db'), ('name_data/names_merged.xlsx', 'name_data/names_marged.xlsx')],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='addon_pack_interface',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=True )
