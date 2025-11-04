secret = pm.collectionVariables.get("app_secret")

function objKeySort(obj) {
    var newKey = Object.keys(obj).sort()
    var newObj = {}
    for (var i = 0; i < newKey.length; i++) {
        newObj[newKey[i]] = obj[newKey[i]]
    }
    return newObj
}

function getEnvVar(k) {
    var v = pm.variables.get(k)
    if (v != null) {
        return v
    }
    v = pm.environment.get(k)
    if (v != null) {
        return v
    }
    v = pm.globals.get(k)
    if (v != null) {
        return v
    }
    return null
}

var ts = Date.parse(new Date()) / 1000
pm.variables.set("timestamp", ts)

calSign = function(secret) {
    var ts = getEnvVar("timestamp")
    var queryParam = pm.request.url.query.members
    var param = {}
    for (var item in queryParam) {
        if (queryParam[item].key == "timestamp") {
            v = ts
        } else {
            var v = queryParam[item].value
            if (v == null || v == "{{" + queryParam[item].key + "}}") {
                v = getEnvVar(queryParam[item].key)
            }
        }
        param[queryParam[item].key] = interpolateVar(v)
    }

    delete param["sign"]
    delete param["access_token"]
    var sortedObj = objKeySort(param)
    var signstring = secret + pm.request.url.getPath()
    for (var key in sortedObj) {
        signstring = signstring + key + sortedObj[key]
    }
    signstring = signstring + interpolateVar(pm.request.body.toString()) +  secret
    console.log(signstring)
    sign = CryptoJS.HmacSHA256(signstring, secret).toString()
    return sign
}

function interpolateVar (value) {
    const {Property} = require('postman-collection')
    return Property.replaceSubstitutions(value, pm.variables.toObject())
}

var sign = calSign(secret)
pm.variables.set("sign", sign)
