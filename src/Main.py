from gui import Ui_MainWindow
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QTableWidgetItem
import numpy as np
import math
import matplotlib as plt
import pyqtgraph as pg
import os
import sys
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import logging
import datetime as dt
import time
from functions import Function


class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        super(MplCanvas, self).__init__(self.fig)


class Error_Map_Thread(QtCore.QThread):
    counter_signal = QtCore.pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)

    def run(self):
        print('Starting thread...')
        cnt = 0
        while cnt < 101:
            print("inside while")
            time.sleep(0.5)
            self.counter_signal.emit(cnt)
            print("emitt " + str(cnt))
            cnt += 5

    def stop(self):
        print('Stopping thread...')
        self.terminate()


class CurveFitting_GUI(Ui_MainWindow):
    def setupUi(self, MainWindow):
        super().setupUi(MainWindow)
        self.set_widget_value()
        self.progressBar.setVisible(False)
        self.progressBar.setRange(0, 100)
        self.progressBar.setValue(0)
        self.vertical_axis_comboBox.addItem("                             ")
        self.vertical_axis_comboBox.addItem("                             ")

    def set_widget_value(self):
        self.fitting_order_SpinBox.setValue(1)
        self.no_chunks_SpinBox.setValue(0)
        self.sig_clip_Slider.setValue(40)
        self.error_map_Button.setStyleSheet("background-color : green")


class Signals:
    def __init__(self, time=None, y_value=None):
        self.signal = [time, y_value]
        self.clipped_signal = [time, y_value]

    def setSignal(self, time, y_value):
        self.signal[0] = time
        self.signal[1] = y_value

    def set_clipped_signal(self, percentage):
        new_len = int(self.get_signal_length() * percentage)
        self.clipped_signal[0] = self.signal[0][:new_len]
        self.clipped_signal[1] = self.signal[1][:new_len]

    def get_clipped_signal(self):
        return (self.clipped_signal[0], self.clipped_signal[1])

    def getSignal(self):
        return (self.signal[0], self.signal[1])

    def get_signal_length(self):
        return len(self.signal[0])

    def get_clipped_sig_len(self):
        return len(self.clipped_signal[0])


class CurveFitting_Application(QtWidgets.QMainWindow):
    Error_Image = None

    def __init__(self):
        super().__init__()
        self.today = dt.datetime.today()
        self.logger = logging.getLogger("NEURALLOGGER")
        logging.basicConfig(filename=f"{self.today.month:02d}-{self.today.day:02d}-{self.today.year}.log",
                            filemode='a',
                            format="%(asctime)s: %(levelname)s-%(message)s",
                            datefmt='%H:%M:%S',
                            level=logging.DEBUG)
        self.signal = None
        self.gui = CurveFitting_GUI()
        self.gui.setupUi(self)
        self.set_widget_function()
        self.map_thread = Error_Map_Thread()

    def set_widget_function(self):
        # Menu Bar:
        self.gui.actionSignal.triggered.connect(self.open_sig_file)

        # Spin Box:
        self.gui.no_chunks_SpinBox.valueChanged.connect(lambda: self.plot_signals(0))
        self.gui.fitting_order_SpinBox.valueChanged.connect(
            lambda: self.plot_signals(1) if self.gui.enable_extrapol_checkBox.isChecked() else self.plot_signals(0))

        # Combo Box:
        self.gui.horizontal_axis_comboBox.activated.connect(self.set_option)
        self.gui.vertical_axis_comboBox.activated.connect(self.set_combo_constant)
        # Check Box:
        self.gui.enable_extrapol_checkBox.stateChanged.connect(self.set_checkBox)

        # Slider:
        self.gui.sig_clip_Slider.valueChanged.connect(lambda: self.plot_signals(1))
        self.gui.constant_value_Slider.valueChanged.connect(
            lambda: self.gui.const_slider_val_label.setText(str(self.gui.constant_value_Slider.value())))

        # Push Button:
        self.gui.error_map_Button.clicked.connect(self.set_Button_func)

    def set_combo_constant(self):
        if self.gui.vertical_axis_comboBox.currentIndex() == 0:
            self.gui.constant_value_label.setText(self.gui.vertical_axis_comboBox.itemText(1))
        else:
            self.gui.constant_value_label.setText(self.gui.vertical_axis_comboBox.itemText(0))

    def set_option(self):
        self.gui.vertical_axis_comboBox.setEnabled(True)
        if self.gui.horizontal_axis_comboBox.currentText() == "Overlap Percentage":
            self.gui.vertical_axis_comboBox.setItemText(0, "Number of Chunks")
            self.gui.vertical_axis_comboBox.setItemText(1, "Order")
        if self.gui.horizontal_axis_comboBox.currentText() == "Order":
            self.gui.vertical_axis_comboBox.setItemText(0, "Number of Chunks")
            self.gui.vertical_axis_comboBox.setItemText(1, "Overlap Percentage")
        if self.gui.horizontal_axis_comboBox.currentText() == "Number of Chunks":
            self.gui.vertical_axis_comboBox.setItemText(0, "Overlap Percentage")
            self.gui.vertical_axis_comboBox.setItemText(1, "Order")

    def set_Button_func(self):
        if self.gui.error_map_Button.text() == "Create":
            self.logger.info("Create button is pressed.")
            self.gui.error_map_Button.setText("Cancel")
            self.gui.error_map_Button.setStyleSheet("background-color : red")
            self.gui.progressBar.setValue(0)
            self.gui.progressBar.setVisible(True)
            self.map_thread.counter_signal.connect(self.error_map)
            self.logger.critical('Starting error map thread...')
            self.map_thread.start()
        else:
            self.logger.info("Cancel button is pressed.")
            self.logger.critical('Ending error map thread...')
            self.map_thread.stop()
            if CurveFitting_Application.Error_Image != None:
                CurveFitting_Application.Error_Image.fig.clear()
            self.gui.error_map_Button.setText("Create")
            self.gui.error_map_Button.setStyleSheet("background-color : green")
            self.gui.progressBar.setVisible(False)

    def open_sig_file(self):
        self.gui.set_widget_value()
        try:
            files_name = QFileDialog.getOpenFileName(self, 'Open only txt or CSV or xls', os.getenv('HOME'),
                                                     "(*.csv *.txt *.xls)")
            path = files_name[0]
            Signal_Name = path.split('/')[-1].split(".")[0]
            data = np.genfromtxt(path, delimiter=',')
            time = list(data[1:, 0])
            y_axis = list(data[1:, 1])
            self.logger.info("Plotting signal from open function.")
            self.signal = Signals(time, y_axis)
            self.gui.Signal_graphicsView.clear()
            self.gui.Signal_graphicsView.plot(time, y_axis, pen='r', name=Signal_Name)
            self.gui.Signal_graphicsView.setXRange(0, np.max(time), padding=0)


            self.gui.add_row_equation(0, 0, 0, 0)
            self.gui.enable_extrapol_checkBox.setCheckState(False)
        except:
            pass

    def set_checkBox(self):
        self.gui.set_widget_value()
        if self.gui.enable_extrapol_checkBox.isChecked():
            self.logger.info("Inside extrapolation mode.")
            self.gui.sig_clip_Slider.setEnabled(True)
            self.gui.no_chunks_SpinBox.setEnabled(False)
            self.plot_signals(1)

        else:
            self.logger.info("Inside interpolation mode.")
            self.gui.sig_clip_Slider.setEnabled(False)
            self.gui.no_chunks_SpinBox.setEnabled(True)
            self.plot_signals(0)

    def plot_clipped_sig(self):
        clipp_percent = self.gui.sig_clip_Slider.value()
        self.gui.clipp_val_label.setText(str(clipp_percent) + " %")
        clipp_percent /= 100
        self.signal.set_clipped_signal(clipp_percent)
        clipped_time, clipped_y = self.signal.get_clipped_signal()
        item = pg.InfiniteLine(pos=clipped_time[-1], pen='g')
        self.gui.Signal_graphicsView.addItem(item)
        return (clipped_time, clipped_y)

    def get_chunks(self):
        no_of_chunks = self.gui.no_chunks_SpinBox.value()
        if no_of_chunks == 0:
            return ([], [])
        time, y_value = self.signal.getSignal()
        time_chunks = np.array_split(time, no_of_chunks)
        y_chunks = np.array_split(y_value, no_of_chunks)
        for index in range(1, len(time_chunks)):
            time_chunks[index] = np.insert(time_chunks[index], 0, time_chunks[index - 1][-1])
            y_chunks[index] = np.insert(y_chunks[index], 0, y_chunks[index - 1][-1])
        return (time_chunks, y_chunks)

    def plot_signals(self, flag):
        self.gui.Signal_graphicsView.clear()
        order = self.gui.fitting_order_SpinBox.value()
        time, y_value = self.signal.getSignal()

        if flag == 0:
            time_chunks, y_chunks = self.get_chunks()
            length = len(time_chunks)
        elif flag == 1:
            clipped_time, clipped_y = self.plot_clipped_sig()
            time_chunks = [clipped_time]
            y_chunks = [clipped_y]
            length = 1
        self.gui.Signal_graphicsView.plot(time, y_value, pen='r')
        error, error1 = self.interpolation(length, order, 0)
        for index in range(0, length):
            coef = np.polyfit(time_chunks[index], y_chunks[index], order)
            equation = Function.function(order, coef)
            self.gui.add_row_equation(length, index, equation, str(round(error1[index], 3)))
            if flag == 1:
                time_chunks[index] = time
            polyval_fn = np.polyval(coef, np.linspace(min(time_chunks[index]), np.max(time_chunks[index]), 100))
            fitted_item = pg.ScatterPlotItem(np.linspace(min(time_chunks[index]), np.max(time_chunks[index]), 100),
                                             polyval_fn, pen="b")
            self.gui.Signal_graphicsView.addItem(fitted_item)
            if index < length - 1:
                item = pg.InfiniteLine(pos=np.max(time_chunks[index]), pen='g')
                self.gui.Signal_graphicsView.addItem(item)

    def error_map(self, counter):
        self.gui.progressBar.setValue(counter)
        if counter == 95:
            self.gui.progressBar.setValue(counter)
            const = self.gui.constant_value_Slider.value()
            horizontal = self.gui.horizontal_axis_comboBox.currentText()
            vertical = self.gui.vertical_axis_comboBox.currentText()
            if (horizontal == "Number of Chunks" and vertical == "Order") or (horizontal == "Order" and vertical == "Number of Chunks"):
                flag = 0
                array = self.calc_error(flag, const / 100)
                if horizontal == "Order" and vertical == "Number of Chunks":
                    array = np.transpose(array)
                self.Draw(array,horizontal,vertical)
        
            elif (horizontal == "Number of Chunks" and vertical == "Overlap Percentage") or (horizontal == "Overlap Percentage" and vertical == "Number of Chunks"):
                flag = 1
                array = self.calc_error(flag, const)
                if horizontal == "Overlap Percentage" and vertical == "Number of Chunks":
                    array = np.transpose(array)
                self.Draw(array,horizontal,vertical)
            
            elif (horizontal == "Order" and vertical == "Overlap Percentage") or (horizontal == "Overlap Percentage" and vertical == "Order"):
                flag = 2
                array = self.calc_error(flag, const)
                if horizontal == "Overlap Percentage" and vertical == "Order":
                    array = np.transpose(array)
                self.Draw(array,horizontal,vertical)

    def calc_error(self, flag, const):
        arry2 = []
        if flag == 0:
            for chunk in range(0, 10):
                array = []
                for order in range(0, 10):
                    # error = 1
                    error, error1 = self.interpolation(chunk + 1, order + 1, const)
                    array.append(error)
                arry2.append(array)
            return arry2
        if flag == 1:
            for chunk in range(0, 10):
                array = []
                for overlap in range(0, 10):
                    # error = 1
                    error, error1 = self.interpolation(chunk + 1, const, overlap * 0.025)
                    array.append(error)
                arry2.append(array)
            return arry2
        if flag == 2:
            for order in range(0, 10):
                array = []
                for overlap in range(0, 10):
                    # error = 1
                    error, errr1 = self.interpolation(const, order, overlap * 0.025)
                    array.append(error)
                arry2.append(array)
            return arry2

    def Draw(self, Array_error,horizontal,vertical):

        Array_error = np.array(Array_error)
        Array_error= np.flip(Array_error,axis=1)
        Error_map_image = MplCanvas(self, 5, 4, 100)
        Error_map_image.axes.imshow(Array_error, cmap='viridis')
        Error_map_image.axes.set_xticks([])
        Error_map_image.axes.set_yticks([])
        Error_map_image.axes.set_xlabel(horizontal)
        Error_map_image.axes.set_ylabel(vertical)
        Error_map_image.axes.set_title("Error Map")



        for x in range(0, Array_error.shape[0]):
            for y in range(0, Array_error.shape[1]):
                Error_map_image.axes.text(x, y, Array_error[x, y],
                                          ha="center", va="center", color="w")
        CurveFitting_Application.Error_Image = Error_map_image
        self.gui.gridLayout.addWidget(Error_map_image, 0, 0, 1, 1)

    def interpolation(self, no_of_chunks, order, overlap_per):
        no_of_chunks = int(no_of_chunks)
        order = int(order)
        if no_of_chunks == 0:
            raise Exception("There must be at least one chunk!!!!")
        else:

            error_list = []
            time_chunks = [[]] * no_of_chunks
            y_chunks = [[]] * no_of_chunks
            time, y_value = self.signal.getSignal()
            Len_Chunck = int(np.ceil(len(time) / (no_of_chunks - (no_of_chunks - 1) * overlap_per)))
            time_chunks[0] = time[0:Len_Chunck]
            y_chunks[0] = y_value[0:Len_Chunck]
            overlap_points = int(np.ceil(Len_Chunck * overlap_per))
            for index in range(1, no_of_chunks):
                start = time.index(time_chunks[index - 1][-1]) - overlap_points
                end = start + Len_Chunck + 1
                if index == no_of_chunks - 1:
                    time_chunks[index] = time[start:len(time)]
                    y_chunks[index] = y_value[start:len(y_value)]
                    break
                time_chunks[index] = time[start:end]
                y_chunks[index] = y_value[start:end]
            sum = 0
            for index in range(0, len(time_chunks)):
                coef = np.polyfit(time_chunks[index], y_chunks[index], order)
                polyval_fn = np.polyval(coef, time_chunks[index])
                sum1 = 0
                for counter in range(0, len(time_chunks[index])):
                    if y_chunks[index][counter] == 0:
                        sum += ((y_chunks[index][counter] - polyval_fn[counter]) ) ** 2
                        sum1 += ((y_chunks[index][counter] - polyval_fn[counter])) ** 2

                        continue
                    sum += ((y_chunks[index][counter] - polyval_fn[counter]) / y_chunks[index][counter]) ** 2
                    sum1 += ((y_chunks[index][counter] - polyval_fn[counter]) / y_chunks[index][counter]) ** 2
                error = math.sqrt(sum1 / len(time_chunks[index]))
                error_list.append(error)
            error = math.sqrt(sum / len(time))
            return round(error, 2), error_list


def window():
    app = QApplication(sys.argv)
    win = CurveFitting_Application()
    win.show()
    sys.exit(app.exec_())


# main code
if __name__ == "__main__":
    window()
