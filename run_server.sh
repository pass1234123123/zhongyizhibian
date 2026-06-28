export PYTHONPATH=$HOME/.local/lib/python3.12/site-packages:$PYTHONPATH
cd $HOME/zhongyizhiban
python3 -c "import sys; sys.path.insert(0, '$HOME/.local/lib/python3.12/site-packages'); import flask; print('Flask OK:', flask.__version__)"
export PYTHONPATH=$HOME/.local/lib/python3.12/site-packages:$PYTHONPATH
cd $HOME/zhongyizhiban
python3 run.py 2>&1 &
sleep 2
echo "Server PID: $!"
curl -s http://127.0.0.1:5000/api/categories | head -c 100
export PYTHONPATH=$HOME/.local/lib/python3.12/site-packages:$PYTHONPATH
cd $HOME/zhongyizhiban
python3 -c "exec(chr(105)+chr(109)+chr(112)+chr(111)+chr(114)+chr(116)+chr(32)+chr(115)+chr(121)+chr(115))+chr(59)+sys.path.insert(0,chr(34)+chr(36)+chr(72)+chr(79)+chr(77)+chr(69)+chr(47)+chr(46)+chr(108)+chr(111)+chr(99)+chr(97)+chr(108)+chr(47)+chr(108)+chr(105)+chr(98)+chr(47)+chr(112)+chr(121)+chr(116)+chr(104)+chr(111)+chr(110)+chr(51)+chr(46)+chr(49)+chr(50)+chr(47)+chr(115)+chr(105)+chr(116)+chr(101)+chr(45)+chr(112)+chr(97)+chr(99)+chr(107)+chr(97)+chr(103)+chr(101)+chr(115)+chr(34))+chr(59)+from app import app; app.run(host='0.0.0.0', port=5000, debug=False)"
