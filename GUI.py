from PIL import ImageTk, Image
import tkinter as tk
import tkinter.font as font
from tkinter import filedialog
import os
import copy
import pandas as pd

class MainWindow(tk.Frame):
    def __init__(self, root):
        tk.Frame.__init__(self, root)
        self.w = 1600
        self.h = 1000
        
        self.root = root
        self.font_bt = font.Font(family="HY엽서M", size=14)

        self.dir_path = None
        self.file_list = None
        self.current_dir = '/'

        self.image_extensions = ('.png', '.jpg', '.jpeg'
                                '.PNG', '.JPG', '.JPEG')


        #Index of current from image filename list
        self.current_index = 0
        self.current_image = None

        #Image FileName List
        self.file_list = None

        #key : file_name, value : {x: x_value, y: y_value}
        self.labeling_data = {}

        self.Init()
        self.InitComponent()

    #프레임 관련 초기화 함수
    def Init(self):
        x = (self.root.winfo_screenwidth() // 2) - (self.w // 2)
        y = (self.root.winfo_screenheight() // 2) - (self.h // 2)

        self.root.title("Key Point Labeling")
        self.root.geometry("%dx%d+%d+%d" % (self.w, self.h, x, y))
        self.root.resizable(False, False)

        self.root.bind("<Left>", lambda _: self.Left())
        self.root.bind("<Right>", lambda _: self.Right())


    def InitComponent(self):
        self.frame_back = tk.Frame(self.root, bg="#0000A0", width=self.w, height=self.h, relief="solid", borderwidth=1)
        self.frame_back.pack(fill="both", expand="YES")

        self.frame_back.columnconfigure(0, weight=4)
        self.frame_back.columnconfigure(1, weight=1)

        self.frame_left = tk.Frame(self.frame_back, bg="#A00000")
        self.frame_left.grid(row=0, column=0, sticky="nswe")
        self.frame_right = tk.Frame(self.frame_back, bg="#bdd7f0")
        self.frame_right.grid(row=0, column=1, sticky="nswe")

        #캔버스 -> 이미지 보기 및 작업
        self.canvas = tk.Canvas(self.frame_left, width=self.w*0.8, height=self.h)
        self.canvas.pack(fill="both", expand="YES")
        self.canvas.bind("<Button-1>", self.LeftClick)

        self.current_image  = ImageTk.PhotoImage(file="./cat.jpg")
        self.canvas.create_image( (0, 0), anchor="nw", image=self.current_image)

        #0번째 행 -> 폴더선택
        self.bt_folder = tk.Button(self.frame_right, text="폴더선택", font=self.font_bt, command=self.SelectFolder)
        self.bt_folder.grid(row=0, column=0, pady=10, columnspan=2)

        #1, 2번째 행 -> 클릭 된 X, Y 좌표 알려주기
        self.txt_x = tk.Label(self.frame_right, text="x축 : ", font=self.font_bt, bg="#bda7d0")
        self.txt_x.grid(row=1, column=0, padx=20, pady=10)

        self.txt_y = tk.Label(self.frame_right, text="y축 : ", font=self.font_bt, bg="#bda7d0")
        self.txt_y.grid(row=2, column=0, padx=20, pady=10)


        #3, 4번째행 -> 넘기기
        self.bt_left = tk.Button(self.frame_right, text="<", font=self.font_bt, bg="#bda7d0", command=self.Left)
        self.bt_left.grid(row=3, column=0, pady=50)

        self.bt_right = tk.Button(self.frame_right, text=">", font=self.font_bt, bg="#bda7d0", command=self.Right)
        self.bt_right.grid(row=3, column=2, pady=50)

        self.txt_index = tk.Label(self.frame_right, text="/", font=self.font_bt, bg="#bda7d0")
        self.txt_index.grid(row=4, column=0, columnspan=2)

        #마지막행 -> CSV로 저장하기
        self.bt_csv = tk.Button(self.frame_right, text="CSV로 보내기", font=self.font_bt, bg="#bda7d0", command=self.ToCsv)
        self.bt_csv.grid(row=5, column=0, pady=20, columnspan=2)


    #작업할 폴더 선택
    def SelectFolder(self):
        try:
            self.dir_path = filedialog.askdirectory(parent=self.root, initialdir=self.current_dir, title='Please select a directory')

            #Set Current Directory -> Change selected directory's parent dir
            parent_dir = self.dir_path.split("/")[:-1]
            self.current_dir = ""
            for dir in parent_dir:
                self.current_dir += dir + "/"
            
            self.current_index = 0
            self.labeling_data = {}
            self.GetImageList()
            self.ReleaseIndex()
            self.ShowImage()
        except Exception as e:
            print(e)
            return

    #선택된 폴더로부터 이미지파일만 가져옴
    def GetImageList(self):
        self.file_list = os.listdir(self.dir_path)

        tmp = []

        for file in self.file_list:
            if file.endswith(self.image_extensions):
                tmp.append(file)

        self.file_list = copy.deepcopy(tmp)

    #Canvas에서 좌클릭시 이벤트 발생
    def LeftClick(self, event):
        current_file_name = self.file_list[self.current_index]
        self.labeling_data[current_file_name] = [event.x, event.y]
        
        print(self.labeling_data)

        self.ShowImage()
    
    #Canvas에 이미지 그려주기
    def ShowImage(self):
        self.canvas.delete("all")
        current_file_name = self.file_list[self.current_index]
        image_path = self.dir_path + '/' + current_file_name
        current_image = Image.open(image_path)
        # current_image = current_image.resize( (int(self.w*0.8), int(self.h) ), Image.ANTIALIAS)
        self.current_image = ImageTk.PhotoImage(current_image)
        self.canvas.create_image(0, 0, image=self.current_image, anchor="nw")

        self.ShowCoordinate()
        self.ReleaseXYLabel()

    #Canvas에 점 찍기
    def ShowCoordinate(self):
        current_file_name = self.file_list[self.current_index]
        if current_file_name in self.labeling_data.keys():
            x = self.labeling_data[current_file_name][0]
            y = self.labeling_data[current_file_name][1]
            self.canvas.create_oval(x-5, y-5, \
                                    x+5, y+5, \
                                    fill="#AA00AA")

    #X, Y라벨을 새로고침
    def ReleaseXYLabel(self):
        current_file_name = self.file_list[self.current_index]
        if current_file_name in self.labeling_data.keys():
            x = self.labeling_data[current_file_name][0]
            y = self.labeling_data[current_file_name][1]

            self.txt_x['text'] = f"X축 : {x}"
            self.txt_y['text'] = f"Y축 : {y}"
        else:
            self.txt_x['text'] = f"X축 : "
            self.txt_y['text'] = f"Y축 : "


    #인덱스 라벨의 텍스트를 새로고침
    def ReleaseIndex(self):
        self.txt_index['text'] =  f"{str(self.current_index+1)} / {str(len(self.file_list))}"

    #이전 인덱스로
    def Left(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.ReleaseIndex()
            self.ShowImage()

    #다음 인덱스로
    def Right(self):
        if self.current_index < len(self.file_list)-1:
            self.current_index += 1
            self.ReleaseIndex()
            self.ShowImage()

    #CSV Export
    def ToCsv(self):
        #Labeling이 모두 되었을 경우
        if len(self.labeling_data.keys()) == len(self.file_list):
            if os.path.exists("result.csv"):
                tk.messagebox.showwarning("실패", "result.csv가 존재합니다")
            else:
                try:
                    df = pd.DataFrame.from_dict(self.labeling_data, orient='index', columns=['x', 'y'])
                    df.to_csv("result.csv", sep=',', encoding="utf-8-sig")
                    tk.messagebox.showinfo("성공", f"{len(self.labeling_data.keys())}개의 이미지 파일에 대한 라벨링 성공\nresult.csv 확인")
                except Exception as e:
                    tk.messagebox.showwarning("실패", e)
        else:
            tk.messagebox.showwarning("실패", "라벨링이 덜 된 것 같습니다")
