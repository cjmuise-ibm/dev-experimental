TIMEOUT=10

python3 policy_summarization.py --filename domains/blocksworld-new/p1.json --timeout $TIMEOUT > /dev/tty
python3 policy_summarization.py --filename domains/blocksworld-new/p2.json --timeout 10 > /dev/tty
python3 policy_summarization.py --filename domains/blocksworld-new/p3.json --timeout 10 > /dev/tty

python3 policy_summarization.py --filename domains/elevators/p1.json --timeout 10 > /dev/tty
python3 policy_summarization.py --filename domains/elevators/p2.json --timeout 10 > /dev/tty
python3 policy_summarization.py --filename domains/elevators/p3.json --timeout 10 > /dev/tty

python3 policy_summarization.py --filename domains/tiny-triangle-tireworld/p1.json --timeout 10 > /dev/tty
python3 policy_summarization.py --filename domains/tiny-triangle-tireworld/p2.json --timeout 10 > /dev/tty
python3 policy_summarization.py --filename domains/tiny-triangle-tireworld/p3.json --timeout 10 > /dev/tty

python3 policy_summarization.py --filename domains/traffic-light/p1.json --timeout 10 > /dev/tty
python3 policy_summarization.py --filename domains/traffic-light/p2.json --timeout 10 > /dev/tty
python3 policy_summarization.py --filename domains/traffic-light/p3.json --timeout 10 > /dev/tty

python3 policy_summarization.py --filename domains/triangle-tireworld/p1.json --timeout 10 > /dev/tty
python3 policy_summarization.py --filename domains/triangle-tireworld/p2.json --timeout 10 > /dev/tty
python3 policy_summarization.py --filename domains/triangle-tireworld/p3.json --timeout 10 > /dev/tty
