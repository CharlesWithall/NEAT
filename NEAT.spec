# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['NEAT.py'],
             pathex=['venv\\Lib\\site-packages', 'F:\\Code\\Python\\AssessmentModel'],
             binaries=[],
             datas=[('default_save_data.json', '.'), ('NEAT.ico', '.')],
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
          name='NEAT',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False , icon='NEAT.ico')
