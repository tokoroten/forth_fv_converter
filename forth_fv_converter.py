#coding: utf-8
import re
import math
import sys

def access_dict_by_json(target_dict, accessor):
    try:
        return float(accessor)
    except:
        pass

    if accessor[0] == accessor[-1]:
        if accessor[0] in ('"', "'"):
            return accessor[1:-1]

    obj = target_dict
    splited_accessor = re.split(r"[\.\[\]]", accessor)
    for item in splited_accessor:
        if item == '':
            continue

        try:
            if item.isdigit():
                obj = obj[int(item)]
            else:
                obj = obj[item]
        except:
            return 0.0
    return obj

class _TinyForth:
    def __init__(self, target_dict, script):
        self.target_dict = target_dict
        self.script_list = re.split('\s+', script.strip())
        self.stack = []
        self.js_code = []
        self.function_list = dir(_TinyForth)

        self.convert_label_short_syntax()

    def convert_label_short_syntax(self):
        if len(self.script_list) == 1:
            if "/" in self.script_list[0]:
                item = self.script_list[0].split("/")
                self.script_list = [item[0], '"%s"' % item[1], "eq"]

    def get_feature(self):
        self.stack = []
        for item in self.script_list:
            if item in self.function_list:
                getattr(self, item)()
            else:
                t = access_dict_by_json(self.target_dict, item)
                self.stack.append(t)
        return self.stack[-1]

    def get_formula(self):
        self.js_code = []
        self.js_code.append("function(target_obj) {")
        self.js_code.append('var t1, t2, t3;')
        self.js_code.append("var stack = new Array();")

        for item in self.script_list:
            item_formula = item + "_formula"
            if item_formula in self.function_list:
                getattr(self, item_formula)()
            else:
                try:
                    float(item)
                    self.js_code.append("stack.push(%s);" % item)
                    continue
                except:
                    pass

                if item[0] == item[-1]:
                    if item[0] in ('"', "'"):
                        self.js_code.append("stack.push(%s);" % item)
                        continue

                self.js_code.append("stack.push(target_obj.%s === undefined ? 0.0 : target_obj.%s);" % (item, item))

        self.js_code.append("return stack.pop();")
        self.js_code.append("}")
        return "\n".join(self.js_code)

    def eq(self):
        t1 = self.stack.pop()
        t2 = self.stack.pop()
        self.stack.append(1 if t1 == t2 else 0)

    def eq_formula(self):
        self.js_code.append("t1 = stack.pop();")
        self.js_code.append("t2 = stack.pop();")
        self.js_code.append("stack.push(t1 == t2 ? 1 : 0);")

    def bool(self):
        t1 = self.stack.pop()
        self.stack.append(1 if t1 else 0)

    def bool_formula(self):
        self.js_code.append("stack.push(stack.pop() ? 1 : 0);")

    def add(self):
        self.stack.append(self.stack.pop() + self.stack.pop())

    def add_formula(self):
        self.js_code.append("stack.push(stack.pop() + stack.pop());")

    def sub(self):
        t1 = self.stack.pop()
        t2 = self.stack.pop()
        self.stack.append(t2 - t1)

    def sub_formula(self):
        self.js_code.append("t1 = stack.pop();")
        self.js_code.append("t2 = stack.pop();")
        self.js_code.append("stack.push(t2 - t1);")

    def mul(self):
        self.stack.append(self.stack.pop() * self.stack.pop())

    def mul_formula(self):
        self.js_code.append("stack.push(stack.pop() * stack.pop());")

    def div(self):
        t1 = self.stack.pop()
        t2 = self.stack.pop()
        self.stack.append(float(t2) / t1)

    def div_formula(self):
        self.js_code.append("t1 = stack.pop();")
        self.js_code.append("t2 = stack.pop();")
        self.js_code.append("stack.push(t2 / t1);")

    def log(self):
        t = self.stack.pop()
        if t > 0:
            self.stack.append(math.log(t))
        else:
            self.stack.append(-744.4400719213812)

    def log_formula(self):
        self.js_code.append("t1 = stack.pop();")
        self.js_code.append("stack.push(t1 > 0 ? Math.log(t1) : -744.4400719213812);")

    def log10(self):
        t = self.stack.pop()
        if t > 0:
            self.stack.append(math.log10(t))
        else:
            self.stack.append(-744.4400719213812)

    def log10_formula(self):
        self.js_code.append("t1 = stack.pop();")
        self.js_code.append("stack.push(t1 > 0 ? Math.log10(t1) : -744.4400719213812);")

    def log1p(self):
        t = self.stack.pop()
        if t > -1:
            self.stack.append(math.log1p(t))
        else:
            self.stack.append(-744.4400719213812)

    def log1p_formula(self):
        self.js_code.append("t1 = stack.pop();")
        self.js_code.append("stack.push(t1 > -1.0 ? Math.log(t1 + 1.0) : -744.4400719213812);")

    def chop(self):
        t = sorted([self.stack.pop(), self.stack.pop(), self.stack.pop()])
        self.stack.append(t[1])

    def chop_formula(self):
        self.js_code.append("t1 = stack.pop();")
        self.js_code.append("t2 = stack.pop();")
        self.js_code.append("t3 = stack.pop();")
        self.js_code.append("stack.push([t1, t2, t3].sort(function(a, b){return a - b})[1]);")

class ForthFVConverter:
    def __init__(self, config_filename = None):
        self.script_list = []
        if config_filename:
            self.load_config(config_filename)

    def load_config(self, config_filename):
        self.script_list = []
        for linedata in open(config_filename):
            linedata = linedata.split("#")[0]   # remove commet
            linedata = linedata.strip()
            if linedata == "":
                continue
            self.script_list.append(linedata)

    def set_script_list(self, script_list = []):
        self.script_list = script_list

    def get_header(self):
        header = []
        for script in self.script_list:
            header.append(re.sub(r'\s+', "_", script))
        return header

    def get_fv(self, target_dict_list):
        feature_vector_list = []
        for target_dict in target_dict_list:
            fv = []
            for script in self.script_list:
                tf = _TinyForth(target_dict, script)
                t = tf.get_feature()
                fv.append(t)
            feature_vector_list.append(fv)

        header = self.get_header()
        return header, feature_vector_list

    def get_formula(self):
        formula_list = []
        for script in self.script_list:
            tf = _TinyForth({}, script)
            t = tf.get_formula()
            formula_list.append(t)

        header = self.get_header()
        return header, formula_list


if __name__ == "__main__":
    target_dict1 = {
        'a': 10,
        'b': 200,
        'c': 50.0,
        'e': {
            'hoge': 1000
        },
        'is_login': True,
    }
    target_dict2 = {
        'a': -50.0,
        'b': 99.0,
        'd': 20.0,
        'piyo_label': 'top',
        'is_login': False,
    }

    def test1():
        script_list = []
        script_list.append('a')
        script_list.append('b')
        script_list.append('c')
        script_list.append('d')
        script_list.append('e.hoge')
        script_list.append('a b add')
        script_list.append('a b sub')
        script_list.append('a b div')
        script_list.append('a c add log1p')
        script_list.append('a b div log1p')
        script_list.append('a 100 200 chop')
        script_list.append('piyo_label "top" eq')
        script_list.append('piyo_label "sale" eq')
        script_list.append('piyo_label/top')    # ラベル変数の省略記法
        script_list.append('is_login bool')    # bool変数を01に変換

        print "from source"
        fvc = ForthFVConverter()
        fvc.set_script_list(script_list)
        header, feature_vector = fvc.get_fv([target_dict1, target_dict2])
        print header
        print feature_vector[0]
        print feature_vector[1]

        header, formula_list = fvc.get_formula()
        for i in xrange(len(header)):
            print header[i], formula_list[i]

    def test2():
        print "from file"
        fvc = ForthFVConverter()
        fvc.load_config('fv_sample.txt')
        header, feature_vector = fvc.get_fv([target_dict1, target_dict2])
        print header
        print feature_vector[0]
        print feature_vector[1]

        header, formula_list = fvc.get_formula()
        for i in xrange(len(header)):
            print header[i], formula_list[i]

    def test3():
        print "js_test"
        def node_test(js_code):
            import subprocess
            node_process = subprocess.Popen(['node'], bufsize=4096,
              stdin=subprocess.PIPE, stdout=subprocess.PIPE, close_fds=True)

            std_out_data, std_err_data =  node_process.communicate(js_code)
            return std_out_data, std_err_data

        import json
        fvc = ForthFVConverter()
        fvc.load_config('fv_sample.txt')
        header, feature_vector = fvc.get_fv([target_dict1])
        header, formula_list = fvc.get_formula()
        target_dict_json = json.dumps(target_dict1)

        for i in xrange(len(header)):
            js_code = "console.log((%s)(%s));\n" % (formula_list[i] , target_dict_json)
            (node_result, node_error) = node_test(js_code)
            try:
                node_result = float(node_result)
            except:
                print 'node_result cant cast to float.', type(node_result), node_result

            diff = node_result - feature_vector[0][i]
            print header[i], feature_vector[0][i], node_result, diff

            # todo: diffが大きかったら何かおかしいのでエラーで落とす

            if node_error:
                # todo: node側でエラーが起こったら、キャッチして落とす
                print node_error

    test1()
    test2()
    test3()
