from qgrec.db_manager import DB
from qgrec.qGRec import MainWindow

if __name__ == "__main__":
    DB.init()
    app = MainWindow()
    app.mainloop()
