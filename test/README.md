# Kivyblocks test

## hello kivyblocks
```
python main.py
```

## script
this is a standalone mode deploy
```
cd test/scrip
python main.py
```

## gadget
[gadget](https://github.com/yumoqing/gadget) is a light wight web server, please read it documents to learn how to install and configure it to run it.
you need to start the gadget and change the port in test/gadget/conf/config.json before to run the following command
### download and run gadget

```
git clone git@github.com/yumoqing/gadget.git
pip install -r requirements.txt
cd gadget/test
python ../src/gadget.py
```
if it run success, gadget is listen on prot 9080, then switch back to kivyblocks folder, then

```
cd test/gadget
python main.py
```

