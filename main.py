import json

# Opening JSON file
f = open('demomodel.json', "r")
# returns JSON object as a dictionary
data = json.load(f)
# Closing file
f.close()

CFacts = [i for n in [[a, 'rv-' + a, 'rv-' + a + '-al', 'rv-' + a + '-rf'] for a in ['rq', 'pm', 'da', 'ac']] for i in n] + ['dc', 'rj', 'ex']
#print(CFacts)

f = open('SH.yaml', "w")
f.write("openapi: 3.0.0\ninfo:\n version: 1.0.0\n title: test\npaths:\n")
for tk in data['transactionkinds']:
    for a in CFacts:
        f.write(f" /{tk['id']}{a}:\n  post:\n   summary: creates a new {tk['id']}-{a}\n   requestBody:\n    required: true\n    content:\n     application/json:\n      schema:\n       $ref: '#/components/schemas/{tk['productname']}'\n")       
        f.write(f"   responses:\n    '201':\n     description: C-fact created\n     content:\n      application\json:\n       schema:\n        $ref: '#/components/schemas/CFact'\n    '400':\n     description: invalid input\n")

for fk in data['factkinds']:
    if fk['type'] == 'entitytype':
        f.write(f" /{fk['name']}/" + "{" + f"{fk['name']}ID" + "}" + f":\n  get:\n   summary: returns {fk['name']} data for given ID if it exists\n   parameters:\n    - in: path\n      name: {fk['name']}ID\n      schema:\n       type: integer\n      required: true\n   responses:\n    '200':\n     description: {fk['name']} found\n     content:\n      application\json:\n       schema:\n        $ref: '#/components/schemas/{fk['name']}'\n    '400':\n     description: {fk['name']} not found\n")
        if fk['focus'] == 'in':
            f.write(f" /{fk['name']}:\n  post:\n   summary: creates {fk['name']}\n   requestBody:\n    required: true\n    content:\n     application/json:\n      schema:\n       $ref: '#/components/schemas/{fk['name']}'\n   responses:\n    '200':\n     description: {fk['name']} created\n     content:\n      application\json:\n       schema:\n        type: integer\n    '400':\n     description: invalid input\n")
    if fk['type'] == 'derived':
        f.write(f" /calculate{fk['name']}:\n  get:\n   summary: returns {fk['name']} data for given input\n   parameters:\n")
        for p in fk['parameters']:
            if ':' in p:
                _, ptype, pname = p.split(':')
                f.write(f"    - in: query\n      name: {pname}\n      schema:\n       type: {ptype}\n      required: true\n")
            else:
                f.write(f"    - in: query\n      name: {p}\n      schema:\n       $ref: '#/components/schemas/{p}'\n      required: true\n")
        f.write(f"   responses:\n    '200':\n     description: {fk['name']} calculated\n     content:\n      application\json:\n       schema:\n")
        if fk['result'].startswith('primitive:'):
            f.write(f"        type: {fk['result'].split(':')[1]}\n")
        else:
            f.write(f"        $ref: '#/components/schemas/{fk['result']}'\n")
        f.write(f"    '400':\n     description: invalid input\n")

for ars in data['actionrules']:
    f.write(f" /assess{ars['id']}/" + "{" + "cactID}" + f":\n  get:\n   summary: evaluates assess part of {ars['id']} for given C-act\n   parameters:\n    - in: path\n      name: cactID\n      schema:\n       type: integer\n      required: true\n   responses:\n    '200':\n     description: assessment performed with result\n     content:\n      application\json:\n       schema:\n        type: integer\n    '400':\n     description: assessment failed\n")
    f.write(f" /response{ars['id']}:\n  post:\n   summary: performs the response part of {ars['id']} for given C-act and decision\n   requestBody:\n    required: true\n    content:\n     application/json:\n      schema:\n       type: object\n       properties:\n        cact:\n         $ref: '#/components/schemas/CFact'\n        decision:\n         type: integer\n   responses:\n    '201':\n     description: response part performed\n     content:\n      application\json:\n       schema:\n        type: array\n        items:\n         type: integer\n    '400':\n     description: performing response part failed\n")

for ar in data['actorroles']:
    f.write(f" /agendaFor{ar['id']}:\n  get:\n   summary: retrieves agenda for {ar['id']}\n   responses:\n    '200':\n     description: agenda for {ar['id']} retrieved\n     content:\n      application\json:\n       schema:\n        type: array\n        items:\n         $ref: '#/components/schemas/CFact'\n")

f.write("components:\n schemas:\n  CFact:\n   type: object\n   properties:\n    performer:\n     type: string\n     example: 'Martin'\n    addressee:\n     type: string\n     example: 'Erik'\n    intention:\n     type: string\n     example: rq\n    product:\n     $ref: '#/components/schemas/ProductKind'\n  ProductKind:\n   type: object\n   oneOf:\n")
for tk in data['transactionkinds']:
    f.write(f"    - type: object\n      properties:\n       {tk['productname']}:\n        $ref: '#/components/schemas/{tk['productname']}'\n")

for tk in data['transactionkinds']:
    f.write(f"  {tk['productname']}:\n   type: object\n   properties:\n")
    for ck in tk['casekinds']:
        f.write(f"    {ck}:\n     $ref: '#/components/schemas/{ck}'\n")
    for fk2 in data['factkinds']:
        if (fk2['type'] == 'propertytype' or fk2['type'] == 'attributetype') and fk2['domain'] == tk['productname']:
            f.write(f"    {fk2['name']}:\n")
            if fk2['type'] == 'propertytype':
                f.write(f"      $ref: '#/components/schemas/{fk2['range']}'\n")
            if fk2['type'] == 'attributetype':
                if fk2['range'].startswith('primitive:'):
                    fk2range = fk2['range'].split(':')[1]
                    if fk2range == 'datetime':
                        f.write(f"     type: string\n     format: date-time\n")
                    else:
                        f.write(f"     type: {fk2range}\n")
                else:
                    f.write(f"      $ref: '#/components/schemas/{fk2['range']}'\n")

for fk in data['factkinds']:
    if fk['type'] == 'valuetype':
        f.write(f"  {fk['name']}:\n")
        if fk['primitive'] == 'datetime':
            f.write(f"     type: string\n     format: date-time\n")
        else:
            f.write(f"   type: {fk['primitive']}\n")
    if fk['type'] == 'entitytype':
        f.write(f"  {fk['name']}:\n   type: object\n   properties:\n")
        for fk2 in data['factkinds']:
            if (fk2['type'] == 'propertytype' or fk2['type'] == 'attributetype') and fk2['domain'] == fk['name']:
                f.write(f"    {fk2['name']}:\n")
                if fk2['type'] == 'propertytype':
                    f.write(f"      $ref: '#/components/schemas/{fk2['range']}'\n")
                if fk2['type'] == 'attributetype':
                    if fk2['range'].startswith('primitive:'):
                        fk2range = fk2['range'].split(':')[1]
                        if fk2range == 'datetime':
                            f.write(f"     type: string\n     format: date-time\n")
                        else:
                            f.write(f"     type: {fk2range}\n")
                    else:
                        f.write(f"      $ref: '#/components/schemas/{fk2['range']}'\n")

f.close()