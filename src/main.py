import os
import bs4
import zipfile
import sys
import shutil
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QMessageBox, QFileDialog
from PyQt5 import QtCore
from PyQt5.QtCore import QFileInfo
from PyQt5.QtGui import QPixmap, QIcon
import design


class MainW(QMainWindow, design.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.choose_file.clicked.connect(self.choose)
        self.choose_img.clicked.connect(self.chimg)
        self.start.clicked.connect(self.work)
        self.directory = None
        self.imgs = None
        self.link = None
        self.herz = None

    def choose(self):
        self.directory = QFileDialog.getExistingDirectory(self, 'Выбрать директорию', '')
        self.directory_line.setText(self.directory)

    def chimg(self):
        self.imgs = QFileDialog.getExistingDirectory(self, 'Выбрать директорию', '')
        self.img_line.setText(self.imgs)

    def work(self):
        self.link = [self.link_1.text(), self.link_2.text(), self.link_3.text(), self.link_4.text(), self.link_5.text(), self.link_6.text()]
        self.herz = self.herz_line.text()
        if self.directory and self.link and self.herz:

            def span_mod(chapter, tags):
                attrs = {}
                s = bs4.BeautifulSoup(chapter, 'html.parser')
                new, content = s.span, []
                if bs4.BeautifulSoup(str(new), 'html.parser').span.attrs and not attrs:
                    attrs = bs4.BeautifulSoup(str(new), 'html.parser').span.attrs
                for i in range(tags.count('span') - 1):
                    old = new
                    new = old.span
                    if bs4.BeautifulSoup(str(new), 'html.parser').span.attrs and not attrs:
                        attrs = bs4.BeautifulSoup(str(new), 'html.parser').span.attrs
                for tg in new.contents:
                    content.append(str(tg))
                for i in range(tags.count('span')):
                    content.insert(0, '<span>')
                    content.append('</span>')
                return content, attrs

            def index(search, tex):
                first = None
                for ele in tex:
                    if str(bs4.BeautifulSoup(ele, 'html.parser')) == search:
                        if not first:
                            first = tex.index(str(ele))
                return first

            def first_tag(texts):
                truth = None
                for ele2 in texts:
                    ele2 = bs4.BeautifulSoup(ele2, 'html.parser')
                    if len(str(ele2.string).split()) > 15 and not truth:
                        truth = ele2
                        return str(truth)
                return None

                # берем текст их полученной строки, меняем его на необходимый текст - получаем необходимую правильно стилизованную строку, остается расставить ее в нужные места

            def chapter_to_str(chapter, links, herz, sdvig):
                try:
                    soup = bs4.BeautifulSoup(chapter, 'html.parser')
                    main_links = [bs4.BeautifulSoup(f'{link}', 'html.parser') if link else None for link in links]
                    main_links2 = list(filter(lambda x: x is not None, main_links))
                    if sdvig < len(main_links2) and sdvig - 1 >= 0:
                        for sd in range(sdvig):
                            sdv = main_links2[sd]
                            main_links2.remove(main_links2[sd])
                            main_links2.append(sdv)
                    else:
                        sdvig = 0
                    sdvig += 1
                    attrs, span, content, f_cont = {}, False, [], []
                    for tg in soup.body.contents:
                        content.append(str(tg))
                    t = [tags.name for tags in soup.find_all()]

                    if 'span' in t and t.count('span') >= 2:
                        try:
                            span = True
                            content, attrs = span_mod(chapter, t)
                        except Exception as e:
                            span = False
                    if 'div' in t and len(content) <= 3 and not span:
                        for el in content:
                            if el != '\n':
                                content = str(el).split('\n')
                                break

                    link = first_tag(content)
                    if link:
                        a = index(link, content)
                        if a:
                            last = (len(content)) // herz
                            if last != 0:
                                counter = 0
                                kth = 0
                                for i in range(a + 1, len(content) + 1, last):
                                    if kth < herz:
                                        if len(main_links2) - 1 >= counter:
                                            content.insert(i, str(main_links2[counter]))
                                            counter += 1
                                        else:
                                            counter = 0
                                            content.insert(i, str(main_links2[0]))
                                    kth += 1
                            else:
                                content.insert(a + 1, str(main_links[0]))
                            truth = bs4.BeautifulSoup(str('\n'.join(content)), 'html.parser')
                            if span:
                                truth = bs4.BeautifulSoup(str(''.join(content)), 'html.parser')
                                soup.span.replace_with(truth)
                                if attrs:
                                    for key, val in attrs.items():
                                        soup.span[f'{key}'] = val
                            else:
                                soup.body.replace_with(truth)
                    return str(soup), sdvig
                except Exception as e:
                    print(e)
                    return None, 0

            a = os.listdir(str(self.directory))
            for el in a:
                with zipfile.ZipFile(f'{str(self.directory)}\{el}') as zf:
                    name = os.path.splitext(el)[0]
                    zf.extractall(f'qwerty/{name}')
                    zf.close()

            c = os.listdir('qwerty')
            for n in c:
                book = f'qwerty\\{n}'
                for_img, metainf = None, None
                items, files = [], []
                for dirpath, _, filenames in os.walk(book):
                    for f in filenames:
                        items.append(os.path.abspath(os.path.join(dirpath, f)))
                        if f == 'content.opf':
                            for_img = os.path.abspath(dirpath)
                            metainf = os.path.abspath(os.path.join(dirpath, f))
                if self.imgs:
                    k = os.listdir(str(self.imgs))
                    with open(metainf, mode='r', encoding='utf-8') as f:
                        a = f.read()
                        soup = bs4.BeautifulSoup(a, 'html.parser')
                        manifest = soup.find('manifest')
                        new_otf = [str(qw) for qw in manifest.contents]
                        for i in range(5):
                            iline = f'<item id="1000{i}" href="{k[i]}" media-type="image/jpeg"/>'
                            new_otf.append(iline)
                        new_otf.append("</manifest>")
                        new_otf.insert(0, '<manifest>')
                        evo = bs4.BeautifulSoup(str('\n'.join(new_otf)), 'html.parser')
                        manifest.replace_with(evo)
                    with open(metainf, mode='w', encoding='utf-8') as f:
                        f.write(str(soup))
                    for el in k:
                        new = shutil.copy(f'{str(self.imgs)}\{el}', for_img)
                        print(new)


                for elem in items:
                    name = os.path.splitext(elem)[1]
                    if name == '.html' or name == '.xhtml':
                        files.append(elem)

                changer = 0
                for file in files:
                        with open(file, mode='r', encoding='utf-8') as f:
                            a = f.read()
                            html, changer = chapter_to_str(a, self.link, int(self.herz), changer)
                            if html:
                                with open(file, mode='w', encoding='utf-8') as f:
                                    f.write(html)
                shutil.make_archive(book, 'zip', f'qwerty\\{n}')

            c = os.listdir('qwerty')
            for i in c:
                if str(os.path.splitext(str(i))[1]) != '.zip':
                    pat = str(os.path.abspath(f'qwerty\\{str(i)}'))
                    a = r'{}'.format(pat)
                    shutil.rmtree(a)
                else:
                    pat = str(os.path.abspath(f'qwerty\\{str(i)}'))
                    base = os.path.splitext(pat)[0]
                    os.rename(pat, base + ".epub")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainW()
    ex.show()
    sys.exit(app.exec_())

