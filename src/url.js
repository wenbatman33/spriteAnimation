// 僅允許完整 HTTP(S) 目的地；拒絕腳本、相對路徑與夾帶登入資料的網址。
export function safeDestination(value){if(typeof value!=='string'||!/^https?:\/\//i.test(value.trim()))return '';try{const url=new URL(value.trim());return ['http:','https:'].includes(url.protocol)&&!url.username&&!url.password?url.href:'';}catch{return '';}}
