export async function load(uri, method = 'GET', file = null) {
	const site_root = 'http://118.42.91.16:11156/';
	let url = new URL(site_root + uri);
	console.log(url);
	let resp;
	if (method == 'GET') {
		resp = await fetch(site_root + uri);
	} else if (method == 'POST') {
		let data = null;
		if (file) {
			data = new FormData();
			data.append('file', file);
		}
		resp = await fetch(site_root + uri, {
			method: 'POST',
			body: data
		});
	}
	let rtn = await resp.json();
	return rtn;
}
