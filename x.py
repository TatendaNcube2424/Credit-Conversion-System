from bleak import BleakScanner

def check_bluetooth_sync():
    """Synchronous Bluetooth status checker for Django"""
    try:
        # Get the event loop and run the async function synchronously
        import asyncio
        devices = asyncio.run(BleakScanner.discover(timeout=1))
        
        result = {
            'status': 'enabled',
            'devices': [{'name': d.name, 'address': d.address} for d in devices]
        }
        print(result)
    except Exception as e:
        print({
            'status': 'disabled',
            'error': str(e)
        })

check_bluetooth_sync()