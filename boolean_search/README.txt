В файле rev_ind.py представлен код с созданием обратного индекса

В файле main.py представлен код с парсингом запроса, построением дерева запросов и потоковой обработкой дерева
Класс RequestTreeLeaf представляет операцию / терм как объект с методами evaluate и goto
Функция parser осуществляет парсинг входного запроса и построение дерева запросов для него
Функция process вызывает parser и обрабатывает дерево, возвращая список из docid для данного запроса

index.sh - создает индекс, принимает путь до архива с данными
search.sh - запускает main, считывает запросы до ввода EOF