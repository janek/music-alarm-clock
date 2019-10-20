import subprocess

def test_areyourunning():
    result = subprocess.run(['curl','localhost:3141/areyourunning'], capture_output=True)
    answer = result.stdout.decode("utf-8") 
    assert answer  == 'YES'
