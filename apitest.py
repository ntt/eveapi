#=============================================================================
# eveapi module demonstration script - Jamie van den Berge
#=============================================================================
#
# This file is in the Public Domain - Do with it as you please.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE
#
#----------------------------------------------------------------------------
# Put your userID and apiKey (full access) here before running this script.
YOUR_USERID = 123456
YOUR_APIKEY = "hPx6rxdYfVNeGcuOgPKRL-ohhithere-aUg6OfxCtMH4FUn5GUzf8YqIQDdc5gF7"

import time
import tempfile
import cPickle
import zlib
import os
from os.path import join, exists
from httplib import HTTPException

import eveapi

api = eveapi.EVEAPIConnection()

#----------------------------------------------------------------------------
print
print "EXAMPLE 1: GETTING THE ALLIANCE LIST"
print " (and showing alliances with 1000 or more members)"
print

# Let's get the list of alliances.
# The API function we need to get the list is:
#
#    /eve/AllianceList.xml.aspx
#
# There is a 1:1 correspondence between folders/files and attributes on api
# objects, so to call this particular function, we simply do this:
result1 = api.eve.AllianceList()

# This result contains a rowset object called "alliances". Rowsets are like
# database tables and you can do various useful things with them. For now
# we'll just iterate over it and display all alliances with more than 1000
# members:
for alliance in result1.alliances:
	if alliance.memberCount >= 1000:
		print "%s <%s> has %d members" %\
			(alliance.name, alliance.shortName, alliance.memberCount)


#-----------------------------------------------------------------------------
print
print "EXAMPLE 2: GETTING WALLET BALANCE OF ALL YOUR CHARACTERS"
print

# To get any info on character/corporation related stuff, we need to acquire
# an authentication context. All API requests that require authentication need
# to be called through this object. While it is possible to call such API
# functions directly through the api object, you would have to specify the
# userID and apiKey on every call. If you are iterating over many accounts,
# that may actually be the better option. However, for these examples we only
# use one account, so this is more convenient.
auth = api.auth(userID=YOUR_USERID, apiKey=YOUR_APIKEY)

# Now let's say you want to the wallet balance of all your characters.
# The API function we need to get the characters on your account is:
#
#    /account/Characters.xml.aspx
#
# As in example 1, this simply means adding folder names as attributes
# and calling the function named after the base page name:
result2 = auth.account.Characters()

# Some tracking for later examples.
rich = 0
rich_charID = 0

# Now the best way to iterate over the characters on your account and show
# the isk balance is probably this way:
for character in result2.characters:
	wallet = auth.char.AccountBalance(characterID=character.characterID)
	isk = wallet.accounts[0].balance
	print character.name, "has", isk, "ISK."

	if isk > rich:
		rich = isk
		rich_charID = character.characterID



#-----------------------------------------------------------------------------
print
print "EXAMPLE 3: WHEN STUFF GOES WRONG"
print

# Obviously you cannot assume an API call to succeed. There's a myriad of
# things that can go wrong:
#
# - Connection error
# - Server error
# - Invalid parameters passed
# - Hamsters died
#
# Therefor it is important to handle errors properly. eveapi will raise
# an AttributeError if the requested function does not exist on the server
# (ie. when it returns a 404), a RuntimeError on any other webserver error
# (such as 500 Internal Server error).
# On top of this, you can get any of the httplib (which eveapi uses) and
# socket (which httplib uses) exceptions so you might want to catch those
# as well.
#

try:
	# Try calling account/Characters without authentication context
	api.account.Characters()
except eveapi.Error, e:
	print "Oops! eveapi returned the following error:"
	print "code:", e.code
	print "message:", e.message
except Exception, e:
	print "Something went horribly wrong:", str(e)
	raise


#-----------------------------------------------------------------------------
print
print "EXAMPLE 4: GETTING CHARACTER SHEET INFORMATION"
print

# We grab ourselves a character context object.
# Note that this is a convenience function that takes care of passing the
# characterID=x parameter to every API call much like auth() does (in fact
# it's exactly like that, apart from the fact it also automatically adds the
# "/char" folder). Again, it is possible to use the API functions directly
# from the api or auth context, but then you have to provide the missing
# keywords on every call (characterID in this case).
#
# The victim we'll use is the last character on the account we used in
# example 1.
me = auth.character(result2.characters[-1].characterID)

# Now that we have a character context, we can display skills trained on
# a character. First we have to get the skill tree. A real application
# would cache this data; all objects returned by the api interface can be
# pickled.
skilltree = api.eve.SkillTree()

# Now we have to fetch the charactersheet.
# Note that the call below is identical to:
#
#   acc.char.CharacterSheet(characterID=your_character_id)
#
# But, as explained above, the context ("me") we created automatically takes
# care of adding the characterID parameter and /char folder attribute.
sheet = me.CharacterSheet()

# This list should look familiar. They're the skillpoints at each level for
# a rank 1 skill. We could use the formula, but this is much simpler :)
sp = [0, 250, 1414, 8000, 45255, 256000]

total_sp = 0
total_skills = 0

# Now the fun bit starts. We walk the skill tree, and for every group in the
# tree...
for g in skilltree.skillGroups:

	skills_trained_in_this_group = False

	# ... iterate over the skills in this group...
	for skill in g.skills:

		# see if we trained this skill by checking the character sheet object
		trained = sheet.skills.Get(skill.typeID, False)
		if trained:
			# yep, we trained this skill.

			# print the group name if we haven't done so already
			if not skills_trained_in_this_group:
				print g.groupName
				skills_trained_in_this_group = True

			# and display some info about the skill!
			print "- %s Rank(%d) - SP: %d/%d - Level: %d" %\
				(skill.typeName, skill.rank, trained.skillpoints, (skill.rank * sp[trained.level]), trained.level)
			total_skills += 1
			total_sp += trained.skillpoints


# And to top it off, display totals.
print "You currently have %d skills and %d skill points" % (total_skills, total_sp)



#-----------------------------------------------------------------------------
print
print "EXAMPLE 5: USING ROWSETS"
print

# For this one we will use the result1 that contains the alliance list from
# the first example.
rowset = result1.alliances

# Now, what if we want to sort the alliances by ticker name. We could unpack
# all alliances into a list and then use python's sort(key=...) on that list,
# but that's not efficient. The rowset objects support sorting on columns
# directly:
rowset.SortBy("shortName")

# Note the use of Select() here. The Select method speeds up iterating over
# large rowsets considerably as no temporary row instances are created.
for ticker in rowset.Select("shortName"):
	print ticker,
print

# The sort above modified the result inplace. There is another method, called
# SortedBy, which returns a new rowset. 

print

# Another useful method of rowsets is IndexBy, which enables you to do direct
# key lookups on columns. We already used this feature in example 3. Indeed
# most rowsets returned are IndexRowsets already if the data has a primary
# key attribute defined in the <rowset> tag in the XML data.
#
# IndexRowsets are efficient, they reference the data from the rowset they
# were created from, and create an index mapping on top of it.
#
# Anyway, to create an index:
alliances_by_ticker = rowset.IndexedBy("shortName")

# Now use the Get() method to get a row directly.
# Assumes ISD alliance exists. If it doesn't, we probably have bigger
# problems than the unhandled exception here -_-
try:
	print alliances_by_ticker.Get("ISD")
except :
	print "Blimey! CCP let the ISD alliance expire -AGAIN-. How inconvenient!"

# You may specify a default to return in case the row wasn't found:
print alliances_by_ticker.Get("123456", 42)

# If no default was specified and you try to look up a key that does not
# exist, an appropriate exception will be raised:
try:
	print alliances_by_ticker.Get("123456")
except KeyError:
	print "This concludes example 5"



#-----------------------------------------------------------------------------
print
print "EXAMPLE 6: CACHING DATA"
print

# For some calls you will want caching. To facilitate this, a customized
# cache handler can be attached. Below is an example of a simple cache
# handler. 

class MyCacheHandler(object):
	# Note: this is an example handler to demonstrate how to use them.
	# a -real- handler should probably be thread-safe and handle errors
	# properly (and perhaps use a better hashing scheme).

	def __init__(self, debug=False):
		self.debug = debug
		self.count = 0
		self.cache = {}
		self.tempdir = join(tempfile.gettempdir(), "eveapi")
		if not exists(self.tempdir):
			os.makedirs(self.tempdir)

	def log(self, what):
		if self.debug:
			print "[%d] %s" % (self.count, what)

	def retrieve(self, host, path, params):
		# eveapi asks if we have this request cached
		key = hash((host, path, frozenset(params.items())))

		self.count += 1  # for logging

		# see if we have the requested page cached...
		cached = self.cache.get(key, None)
		if cached:
			cacheFile = None
			#print "'%s': retrieving from memory" % path
		else:
			# it wasn't cached in memory, but it might be on disk.
			cacheFile = join(self.tempdir, str(key) + ".cache")
			if exists(cacheFile):
				self.log("%s: retrieving from disk" % path)
				f = open(cacheFile, "rb")
				cached = self.cache[key] = cPickle.loads(zlib.decompress(f.read()))
				f.close()

		if cached:
			# check if the cached doc is fresh enough
			if time.time() < cached[0]:
				self.log("%s: returning cached document" % path)
				return cached[1]  # return the cached XML doc

			# it's stale. purge it.
			self.log("%s: cache expired, purging!" % path)
			del self.cache[key]
			if cacheFile:
				os.remove(cacheFile)

		self.log("%s: not cached, fetching from server..." % path)
		# we didn't get a cache hit so return None to indicate that the data
		# should be requested from the server.
		return None

	def store(self, host, path, params, doc, obj):
		# eveapi is asking us to cache an item
		key = hash((host, path, frozenset(params.items())))

		cachedFor = obj.cachedUntil - obj.currentTime
		if cachedFor:
			self.log("%s: cached (%d seconds)" % (path, cachedFor))

			cachedUntil = time.time() + cachedFor

			# store in memory
			cached = self.cache[key] = (cachedUntil, doc)

			# store in cache folder
			cacheFile = join(self.tempdir, str(key) + ".cache")
			f = open(cacheFile, "wb")
			f.write(zlib.compress(cPickle.dumps(cached, -1)))
			f.close()


# Now try out the handler! Even though were initializing a new api object
# here, a handler can be attached or removed from an existing one at any
# time with its setcachehandler() method.
cachedApi = eveapi.EVEAPIConnection(cacheHandler=MyCacheHandler(debug=True))

# First time around this will fetch the document from the server. That is,
# if this demo is run for the first time, otherwise it will attempt to load
# the cache written to disk on the previous run.
result = cachedApi.eve.SkillTree()

# But the second time it should be returning the cached version
result = cachedApi.eve.SkillTree()



#-----------------------------------------------------------------------------
print
print "EXAMPLE 7: TRANSACTION DATA"
print "(and doing more nifty stuff with rowsets)"
print

# okay since we have a caching api object now it is fairly safe to do this
# example repeatedly without server locking you out for an hour every time!

# Let's use the first character on the account (using the richest character
# found in example 2). Note how we are chaining the various contexts here to
# arrive directly at a character context. If you're not using any intermediate
# contexts in the chain anyway, this is okay.
me = cachedApi.auth(YOUR_USERID, YOUR_APIKEY).character(rich_charID)

# Now fetch the journal. Since this character context was created through 
# the cachedApi object, it will still use the cachehandler from example 5.
journal = me.WalletJournal()

# Let's see how much we paid SCC in transaction tax in the first page
# of data!

# Righto, now we -could- sift through the rows and extract what we want,
# but we can do it in a much more clever way using the GroupedBy method
# of the rowset in the result. This creates a mapping that maps keys
# to Rowsets of all rows with that key value in specified column.
# These data structures are also quite efficient as the only extra data
# created is the index and grouping.
entriesByRefType = journal.entries.GroupedBy("refTypeID")

# Also note that we're using a hardcoded refTypeID of 54 here. You're
# supposed to use .eve.RefTypes() though (however they are not likely
# to be changed anyway so we can get away with it)
# Note the use of Select() to speed things up here.
amount = 0.0
date = 0
for taxAmount, date in entriesByRefType[54].Select("amount", "date"):
	amount += -taxAmount

print "You paid a %.2f ISK transaction tax since %s" %\
	(amount, time.asctime(time.gmtime(date)))


# You might also want to see how much a certain item yielded you recently.
typeName = "Expanded Cargohold II"
amount = 0.0

wallet = me.WalletTransactions()
soldTx = wallet.transactions.GroupedBy("transactionType")["sell"]
for row in soldTx.GroupedBy("typeName")[typeName]:
	amount += (row.quantity * row.price)

print "%s sales yielded %.2f ISK since %s" %\
	(typeName, amount, time.asctime(time.gmtime(row.transactionDateTime)))

# I'll leave walking the transaction pages as an excercise to the reader ;)
# Please also see the eveapi module itself for more documentation.

# That's all folks!

