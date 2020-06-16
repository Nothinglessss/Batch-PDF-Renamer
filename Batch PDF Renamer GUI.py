

from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.layout import LAParams
from pdfminer.converter import PDFPageAggregator

import pdfminer


import mojimoji
import io
import os
import shutil

import regex as re
import sys
import fileinput

import pybase64

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


def patterncjk(self):
    pattern_cjk = re.compile(
        r'[\p{IsHan}\p{IsBopo}\p{IsHira}\p{IsKatakana}]', re.UNICODE)
    findall = pattern_cjk.findall(self)
    return findall


def patterneng(self):
    pattern_eng = re.compile(r'[a-zA-Z]')
    findall = re.findall(pattern_eng, self)
    return findall


pdf_path = sys.argv[1]
pdf_path_str = str(pdf_path)
pdf_dir = str(os.path.dirname(pdf_path_str))+"\\"
pdf_dir_new = pdf_dir+"\\new\\"
pdf_basename = str(os.path.basename(pdf_path_str))

if not os.path.exists(pdf_dir_new):
    os.makedirs(pdf_dir_new)

# print (f"・Processing {pdf_basename}...<br/>")


def rename_pdf(pdffile):
    rsrcmgr = PDFResourceManager()
    retstr = io.StringIO()
    laparams = LAParams()
    # ltchar=Extended_LTChar()
    device = PDFPageAggregator(rsrcmgr, laparams=laparams)
    with open(pdffile, "rb") as pdf:
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        for page in PDFPage.get_pages(pdf, check_extractable=False):
            counter = 0
            interpreter.process_page(page)
            counter += 1
            if counter == 1:
                break
        result = device.get_result()

    def parse_obj_char(objs):
        for i, obj in enumerate(objs):
            if isinstance(obj, pdfminer.layout.LTTextBox):
                for o in obj._objs:
                    textchunk = obj.get_text()
                    if isinstance(o, pdfminer.layout.LTTextLine):
                        text = o.get_text()
                        if text.strip():
                            found = 0
                            for c in o._objs:
                                if isinstance(c, pdfminer.layout.LTChar):
                                    c.fontsize = float(c.size)
                                    c.char = c.get_text()
                                    found += 1
                                if found == 1:
                                    yield [c.char, c.fontsize, textchunk]
                                    break
            if i == 10:
                break
            elif isinstance(obj, pdfminer.layout.LTFigure):
                parse_obj_char(obj._objs)
            else:
                pass

    sentence_comparison = []

    for sentence in parse_obj_char(result):
        sentence_comparison.append(sentence)

    unit1counter = []
    for i, unit in enumerate(sentence_comparison):
        if "\n" in unit[2]:
            unit[2] = unit[2].replace("\n", "")
        unit1counter.append(unit[1])

    try:
        target_unit = max(unit1counter)
        target_unit_combiner = []
        target_unit_index = unit1counter.index(target_unit)
        target_unit_combiner.append(target_unit_index)
        for i, unit in enumerate(unit1counter):
            if unit == max(unit1counter):
                target_unit_combiner.append(i)

        target_sentence_combiner = []

        for i in target_unit_combiner:
            if (len(patterncjk(sentence_comparison[i][2]))) > 0:
                if len(patterneng(sentence_comparison[i][2])) < 10:
                    sentence_comparison[i][2] = re.sub(
                        '\s+', '', sentence_comparison[i][2])
            sentence_comparison[i][2].strip()
            target_sentence_combiner.append(sentence_comparison[i][2])

        target_sentence_combiner = list(
            dict.fromkeys(target_sentence_combiner))

        target_sentence = "-".join(target_sentence_combiner)

        target_sentence = mojimoji.zen_to_han(target_sentence, kana=False)

        return target_sentence

    except ValueError as e:
        return None

    pdf.close()
    device.close()
    retstr.close()


same_file = []
scanned = []
no_text = []


res = rename_pdf(pdf_path)
if res != None:
    try:
        with open(pdf_path_str, "r") as f:
            shutil.copy(pdf_path_str, pdf_dir_new+f"{res}.pdf")
            f.close()
        sys.stdout.write(
            f"<p align='left'>・The file <b>{pdf_basename}</b> has been renamed to <b>{res}.pdf</b> in the subfolder 'new'.</p>")

    except shutil.SameFileError as e:
        print(
            f"<p align='left'>・<b> {pdf_basename} </b> cannot be renamed as it is already renamed:.</p>")
    except OSError as e:
        print(
            f"<p align='left'>・<b> {pdf_basename} </b> cannot be renamed. Maybe it is a scanned document or copy function is disabled.</p>")
else:
    print(
        f"<p align='left'>・<b>{pdf_basename} </b> cannot be renamed as no text can be extracted.</p>")
sys.stdout.flush()

# print("These files cannot be renamed as these files are already renamed:")
# print (",".join(same_file))
# print("These files cannot be renamed as these files are scanned documents:")
# print (",".join(scanned))
# print("These files cannot be renamed as no text can be extracted (perhaps protected): ")
# print (",".join(no_text))
# print("Job Complete!")
