# Fandometric

A command line utility for tracking your tumblr following.

Run with the python 3.5 console:

```
>>> cd fandometric
>>> python3.5
>>> import fandometric
>>> fandometric.changes(url, 0, -1)
```

## Downloading Fandometric

If you know how to use git, you can skip this section. 

Otherwise you can download a copy of Fandometric by going to the Download ZIP button on the side of this page. *You do not need to fork this repository unless you intend to modify Fandometric and want to post your changes.*

![Screenshot](screenshots/tutorial_1.png "Downloading Fandometric")

Extract the ZIP file to anywhere on your computer, as long as you know how to `cd` into the directory using a terminal.

## First time use

Fandometric works by taking snapshots of your tumblr following and comparing the changes between them. To do this, Fandometric needs access to your tumblr account. Fandometric can get the required keys for you as long as you give it permission.

You will be prompted for a fandometric passkey. Official fandometric passkeys are currently only available to certain members of the Taylor Swift fandom. *If you do not have one*, you can generate your own unofficial fandometric passkey by [registering](https://www.tumblr.com/oauth/apps) your copy of fandometric separately with tumblr. Doing so will give you your own consumer key and consumer secret which you can plug directly into the `oauth.Consumer()` constructor in `authorize.py` (you will have to modify the source code).

You will then be sent to a tumblr authorization page, and then a localhost page which will probably display in your browser as a page load error.

![Screenshot](screenshots/tutorial_2.png "Authorizing Fandometric")

![Screenshot](screenshots/tutorial_3.png "Retrieving the OAuth verifier")

Paste the `oauth_verifier` (highlighted portion of the url) into the Fandometric prompt. If successful, Fandometric is now linked to your tumblr account and ready to use.

Fandometric will have saved the OAuth keys in a file called `tumblr_keys.txt` so you won’t have to go through this process each time you use it. **Never share your OAuth keys; they are more or less equivalent to your tumblr password.** (And for Meredith’s sake, *do not post your OAuth keys on Github for the whole internet to see*.)

## Usage
Fandometric is a python console application. It can also be loaded as a library. In the top `fandometric` folder, run the following terminal commands to start python and load Fandometric
```
>>> cd fandometric
>>> python3.5
>>> import fandometric
```
The `fandometric.changes` function is a convenience function that downloads the latest follower/following list for your account from tumblr and compares it with itself. Replace `blogname` with the url of your tumblr blog, in quotes (a tumblr url does not include “http://” or “.tumblr.com”).
```
>>> fandometric.changes(<blogname>)
```
To compare with the last saved snapshot (comparing a follower list with itself isn’t terribly useful), include the two comparison index parameters `0, -1`.
```
>>> fandometric.changes(<blogname>, 0, -1)
```

![Screenshot](screenshots/screenshot_3.png "Fandometric usage")

Comparisons will fail when you run Fandometric for the first time and ask it to perform a comparison with a previous snapshot, because it will have nothing to compare your follower/following list to. Snapshots are saved in a directory called `records` and may be freely deleted to clean out your records. Fandometric refers to these files by their numeric indexes.

## Advanced usage
`fandometric.changes` combines two operations—list downloading, and list comparison—that Fandometric provides separately through the functions `fandometric.update` and `fandometric.compare`.

`fandometric.update(url[, directory='records'])`

Fetches the follower and following lists from tumblr and saves the data as `n.txt`, where `n` is one greater than the highest numbered file in `directory`.

* **url** : the tumblr url of your primary blog. *(required)*
* **directory** : the directory Fandometric will save the snapshot in. Must be free of all non-snapshot files.

`fandometric.compare(a=0, b=a, directory='records')`

Compares the `a`th last and `b`th last snapshots in `directory`. The parameters `a` and `b` are counted backwards from the highest numbered file in `directory`. For example, if `1989.txt` is the highest numbered file in `directory`, `0` will refer to `1989.txt` and `-1` will refer to `1988.txt`. `a` and `b` can be in any order; Fandometric will compare the higher number to the lower. If any of the referenced files does not exist, comparison will fail.

* **a** : the reverse index of the first snapshot to compare. Sign is irrelevant; `-1` and `1` are equivalent. Defaults to `0`.
* **b** : the reverse index of the second snapshot to compare. Sign is irrelevant; `-1` and `1` are equivalent. Defaults to the value of `a` (self comparison).
* **directory** : the directory Fandometric will search for `a` and `b` in. Must be free of all non-snapshot files.

![Screenshot](screenshots/screenshot_4.png "Comparison output")

### Comparison output
| lost followers | |
| --- | --- |
| `exists` | the blog currently exists on tumblr |
| `deleted` | the blog no longer exists on tumblr |
| `unknown` | Fandometric was unable to verify the existence of this blog |
| `mutual` | You followed this blog at the time of the second snapshot |
| `—` | You did not follow this blog at the time of the second snapshot |

| gained followers | |
| --- | --- |
| `new` | this blog is a new follower (always `new`)
| `mutual` | You followed this blog at the time of the second snapshot |
| `—` | You did not follow this blog at the time of the second snapshot |

| stats ||
| --- | --- |
| `ratio=u/v (u:v)` | The ratio of followers to following at the time of the second snapshot |
| `p% inactive following (n blogs)` | The proportion and number of inactive blogs that you follow (inactivity defined as greater than one week) |
| `p% inactive followers (n blogs)` | The proportion and number of inactive blogs that follow you (inactivity defined as greater than one week)

`fandometric.following()`

Displays a list of the blogs you are following, sorted by the time they were last active. 

![Screenshot](screenshots/screenshot_5.png "Activity list")
