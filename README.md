# Simple TCP proxy #  

Flags:  
`--help`, `-h`, `-?` - see this msg again  
`--version`, `-v` - print version  
`--host`, `-H` - destination host  
`--post`, `-P` - destination port  
`--listen`, `-l` - port to listen to (default: 8888)  
`--buffer-limit` - size of buffer for readers  

Example:  
Run on server:  
`$ ./proxy.py -H=ya.ru -P=443`  

Run on client:  
`$ curl https://ya.ru -H 'Host: ya.ru' -k`  
