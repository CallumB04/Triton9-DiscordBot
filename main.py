import discord
from discord.ext import commands
from discord.ext.commands import Bot
import asyncio
import json, os

os.chdir("C:\\Users\\toure\\Coding\\Python\\Triton9-DiscordBot")

with open("./data/botinfo.json", "r") as f:
    data = json.load(f)
    TOKEN = data["token"]

bot = commands.Bot(command_prefix="!")

@bot.event
async def on_ready():
    print("Bot Online!\n")

@bot.event
async def on_message(message):
    if not message.author.bot:
    
        bot.remove_command("help")
        await bot.process_commands(message)

@bot.command()
async def team(ctx, choice="", teamname="", *, players=""):
    ## -- choice -- !team <choice>
    ## create -> allows user to create a new team with 4 members maximum
    ## delete -> allows user to delete a team they own ( with two step verification ) 
    ## view -> allows user to view a teams members, owner and stats
    ## add -> allows user to add a team member to a team they own ( if there isnt already 4 )
    ## remove -> allows user to remove a team member from a team they own

    teamname = teamname.lower()

    if players != "":
        teamplayers = []
        players = players.strip()
        if " " in players:
            players = players.split(" ")
            for p in players:
                userid_0 = p.split("!")[1]
                userid = userid_0.split(">")[0]
                player = await bot.fetch_user(int(userid))
                teamplayers.append(player)
        else:
            userid_0 = players.split("!")[1]
            userid = userid_0.split(">")[0]
            player = await bot.fetch_user(int(userid))
            teamplayers.append(player)

    if choice.upper() in ["CREATE", "DELETE", "VIEW", "ADD", "REMOVE"]:
        if choice.upper() == "CREATE":
            if teamname == "":
                await ctx.message.channel.send(f"Please enter a team name. Use '!help' commands if you need! <@{ctx.message.author.id}>")
                return
            elif len(teamplayers) == 0:
                await ctx.message.channel.send(f"Please choose atleast one team member. Use '!help' commands if you need! <@{ctx.message.author.id}>")
                return
            elif len(teamplayers) > 4:
                await ctx.message.channel.send(f"4 Team players max. Please try again! <@{ctx.message.author.id}>")
                return
            
            with open("./data/teams.json", "r") as f:
                teams = json.load(f)

                ## team name and player checks
                for team in teams:
                    if teams[team] == teamname.lower():
                        await ctx.message.channel.send(f"Team name: '{teamname}' is taken. Please choose a different name! <@{ctx.message.author.id}>")
                        return
                    for current_player in teams[team]["players"]:
                        for player in teamplayers:
                            if current_player == player.id:
                                await ctx.message.channel.send(f"<@{player.id}> is already in the team: '{team}'. Use '!player leave' if you wish to leave it! <@{ctx.message.author.id}>")
                                return

            with open("./data/teams.json", "r") as f:
                teams = json.load(f)

                player_ids = [player.id for player in teamplayers]
                player_names = [player.name for player in teamplayers]

                teams[teamname] = {}
                teams[teamname]["players"] = player_ids
                teams[teamname]["games"] = 0
                teams[teamname]["wins"] = 0
                teams[teamname]["losses"] = 0
                teams[teamname]["money_earned"] = 0

            with open("./data/teams.json", "w") as f:
                json.dump(teams, f)
                await ctx.message.channel.send(f"Team '{teamname}' created! Players: {player_names}")

        elif choice.upper() == "DELETE":
            if teamname == "":
                await ctx.message.channel.send(f"Please enter a team name. Use '!help' commands if you need! <@{ctx.message.author.id}>")
                return
            
            with open("./data/teams.json", "r") as f:
                teams = json.load(f)

                if teamname in teams:
                    del teams[teamname]
                    await ctx.message.channel.send(f"Team: '{teamname}' deleted! <@{ctx.message.author.id}>")
                else:
                    await ctx.message.channel.send(f"Team: '{teamname}' does not exist! <@{ctx.message.author.id}>")

            with open("./data/teams.json", "w") as f:
                json.dump(teams, f)

        elif choice.upper() == "VIEW":
            if teamname == "":
                await ctx.message.channel.send(f"Please enter a team name. Use '!help' commands if you need! <@{ctx.message.author.id}>")
                return

            with open("./data/teams.json", "r") as f:
                teams = json.load(f)

                if teamname in teams:
                    players_id = teams[teamname]["players"]
                    players_obj = [await bot.fetch_user(playerid) for playerid in players_id]
                    players = [p.name for p in players_obj]
                    team_as_str = ", ".join(players)

                    embed = discord.Embed(title = teamname.capitalize(), color = discord.Colour.red())
                    embed.add_field(name = "Players", value = team_as_str)
                    embed.add_field(name = "Games Played", value = teams[teamname]["games"], inline = False)
                    embed.add_field(name = "Wins", value = teams[teamname]["wins"], inline = False)
                    embed.add_field(name = "Losses", value = teams[teamname]["losses"], inline = False)
                    embed.add_field(name = "Money Earned", value = teams[teamname]["money_earned"], inline = False)
                    await ctx.message.channel.send(embed=embed)
    else:
        await ctx.message.channel.send(f"Not a viable command. Use '!help' commands if you need! <@{ctx.message.author.id}>")
        return

bot.run(TOKEN)