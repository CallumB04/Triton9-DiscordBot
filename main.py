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

    try:
        player_ids = [player.id for player in teamplayers]
        player_names = [player.name for player in teamplayers]

    except:
        pass

    if choice.upper() in ["CREATE", "DELETE", "VIEW", "ADD", "REMOVE"]:
        if choice.upper() == "CREATE":
            if teamname == "":
                await ctx.message.channel.send(f"Please enter a team name. Use '!help' commands if you need! [<@{ctx.message.author.id}>]")
                return
            elif len(teamplayers) == 0:
                await ctx.message.channel.send(f"Please choose atleast one team member. Use '!help' commands if you need! [<@{ctx.message.author.id}>]")
                return
            elif len(teamplayers) > 4:
                await ctx.message.channel.send(f"4 Team players max. Please try again! [<@{ctx.message.author.id}>]")
                return
            
            with open("./data/teams.json", "r") as f:
                teams = json.load(f)

                ## team name and player checks
                for team in teams:
                    if teams[team] == teamname.lower():
                        await ctx.message.channel.send(f"Team name: '{teamname}' is taken. Please choose a different name! [<@{ctx.message.author.id}>]")
                        return
                    for current_player in teams[team]["players"]:
                        for player in teamplayers:
                            if current_player == player.id:
                                await ctx.message.channel.send(f"<@{player.id}> is already in the team: '{team}'. They can use '!player leave' if they wish to leave it! [<@{ctx.message.author.id}>]")
                                return

            with open("./data/teams.json", "r") as f:
                teams = json.load(f)

                teams[teamname] = {}
                teams[teamname]["players"] = player_ids
                teams[teamname]["owner"] = ctx.message.author.id
                teams[teamname]["games"] = 0
                teams[teamname]["wins"] = 0
                teams[teamname]["losses"] = 0
                teams[teamname]["points"] = 0
                teams[teamname]["money_earned"] = 0

            with open("./data/teams.json", "w") as f:
                json.dump(teams, f)

                if len(teams[teamname]["players"]) == 4:
                    await ctx.message.channel.send(f"Team '{teamname}' created! Players: {player_names} [<@{ctx.message.author.id}>]")
                else:
                    await ctx.message.channel.send(f"Team '{teamname}' created! Players: {player_names}. YOU NEED 4 PLAYERS TO COMPETE! [<@{ctx.message.author.id}>]")

            with open("./data/players.json", "r") as f:
                players = json.load(f)

                for p_id in player_ids:
                    id_str = str(p_id)
                    if id_str in players:
                        players[id_str]["team"] = teamname
                    else:
                        players[id_str] = {}
                        players[id_str]["team"] = teamname
                        players[id_str]["games"] = 0
                        players[id_str]["wins"] = 0
                        players[id_str]["losses"] = 0

            with open("./data/players.json", "w") as f:
                json.dump(players, f)

        elif choice.upper() == "DELETE":
            if teamname == "":
                await ctx.message.channel.send(f"Please enter a team name. Use '!help' commands if you need! [<@{ctx.message.author.id}>]")
                return
            
            with open("./data/teams.json", "r") as f:
                teams = json.load(f)

                if teams[teamname]["owner"] == ctx.message.author.id:
                    if teamname in teams:
                        del teams[teamname]
                        await ctx.message.channel.send(f"Team: '{teamname}' deleted! [<@{ctx.message.author.id}>]")
                    else:
                        await ctx.message.channel.send(f"Team: '{teamname}' does not exist! [<@{ctx.message.author.id}>]")
                        return
                else:
                    await ctx.message.channel.send(f"You are not the owner of team '{teamname}'! [<@{ctx.message.author.id}>]")
                    return

            with open("./data/teams.json", "w") as f:
                json.dump(teams, f)
                await ctx.message.channel.send(f"Team '{teamname}' deleted! Players without team: {player_names} [<@{ctx.message.author.id}>]")

            with open("./data/players.json", "r") as f:
                players = json.load(f)

                for p_id in player_ids:
                    id_str = str(p_id)
                    players[id_str]["team"] = "N/A"

            with open("./data/players.json", "w") as f:
                json.dump(players, f)

        elif choice.upper() == "VIEW":
            if teamname == "":
                await ctx.message.channel.send(f"Please enter a team name. Use '!help' commands if you need! [<@{ctx.message.author.id}>]")
                return

            with open("./data/teams.json", "r") as f:
                teams = json.load(f)

                if teamname in teams:
                    players_id = teams[teamname]["players"]
                    players_obj = [await bot.fetch_user(playerid) for playerid in players_id]
                    players = [p.name for p in players_obj]
                    team_as_str = ", ".join(players)
                    owner_id = teams[teamname]["owner"]
                    owner_user = await bot.fetch_user(owner_id)

                    embed = discord.Embed(title = teamname.capitalize(), color = discord.Colour.red())
                    embed.add_field(name = "Owner", value = owner_user.name, inline = False)
                    embed.add_field(name = "Players", value = team_as_str, inline = False)
                    embed.add_field(name = "Games Played", value = teams[teamname]["games"], inline = False)
                    embed.add_field(name = "Wins", value = teams[teamname]["wins"], inline = False)
                    embed.add_field(name = "Losses", value = teams[teamname]["losses"], inline = False)
                    embed.add_field(name = "Points", value = teams[teamname]["points"], inline = False)
                    embed.add_field(name = "Money Earned", value = teams[teamname]["money_earned"], inline = False)
                    await ctx.message.channel.send(embed=embed)

        elif choice.upper() == "ADD":
            if teamname == "":
                await ctx.message.channel.send(f"Please enter a team name. Use '!help' commands if you need! [<@{ctx.message.author.id}>]")
                return
            elif players == "":
                await ctx.message.channel.send(f"Please mention a user you want to add. Use '!help' commands if you need! [<@{ctx.message.author.id}>]")
                return

            with open("./data/teams.json", "r") as f:
                teams = json.load(f)

                current_plr_count = len(teams[teamname]["players"])

                if teams[teamname]["owner"] == ctx.message.author.id:
                    if teamname in teams:
                        if len(teamplayers) + current_plr_count > 4:
                            await ctx.message.channel.send(f"Only 4 players per team. Current: {current_plr_count}, space for {4 - current_plr_count} more! [<@{ctx.message.author.id}>]")
                            return
                    else:
                        await ctx.message.channel.send(f"Team '{teamname}' doesnt exist. Use '!team create' to create a team! [<@{ctx.message.author.id}>]")
                        return
                        
                    for plr in teamplayers:
                        for team in teams:
                            if plr.id in teams[team]["players"]:
                                await ctx.message.channel.send(f"Player '{plr.name}' already on team '{team}'. Use '!player leave' if you wish to leave! [<@{ctx.message.author.id}>]")
                                return

                    for plr in teamplayers:
                        teams[teamname]["players"].append(plr.id)


                else:
                    await ctx.message.channel.send(f"You are not the owner of team '{teamname}'! [<@{ctx.message.author.id}>]")
                    return

            with open("./data/teams.json", "w") as f:
                json.dump(teams, f)
                player_names = [player.name for player in teamplayers]
                await ctx.message.channel.send(f"Player[s] {player_names} added to {teamname}!")

            with open("./data/players.json", "r") as f:
                players = json.load(f)

                for plr_id in player_ids:
                    id_str = str(plr_id)

                    players[id_str]["team"] = teamname

            with open("./data/players.json", "w") as f:
                json.dump(players, f)
        
        elif choice.upper() == "REMOVE":
            if teamname == "":
                await ctx.message.channel.send(f"Please enter a team name. Use '!help' commands if you need! [<@{ctx.message.author.id}>]")
                return
            elif players == "":
                await ctx.message.channel.send(f"Please mention a user you want to remove. Use '!help' commands if you need! [<@{ctx.message.author.id}>]")
                return

            with open("./data/teams.json", "r") as f:
                teams = json.load(f)

                if teams[teamname]["owner"] == ctx.message.author.id:
                    if teamname in teams:
                        for plr in teamplayers:
                            if plr.id in teams[teamname]["players"]:
                                teams[teamname]["players"].remove(plr.id)
                            else:
                                await ctx.message.channel.send(f"Player '{plr.name}' is not on the team '{team}'! [<@{ctx.message.author.id}>]")
                                return
                    else:
                        await ctx.message.channel.send(f"Team {teamname} does not exist! [<@{ctx.message.author.id}>]")
                        return
                else:
                    await ctx.message.channel.send(f"You are not the owner of team '{teamname}'! [<@{ctx.message.author.id}>]")
                    return   

            with open("./data/teams.json", "w") as f:
                json.dump(teams, f)
                player_names = [player.name for player in teamplayers]
                await ctx.message.channel.send(f"Player[s] {player_names} removed from {teamname}! [<@{ctx.message.author.id}>]")

            with open("./data/players.json", "r") as f:
                players = json.load(f)

                for plr_id in player_ids:
                    id_str = str(plr_id)

                    players[id_str]["team"] = "N/A"

            with open("./data/players.json", "w") as f:
                json.dump(players, f)

    else:
        await ctx.message.channel.send(f"Not a viable command. Use '!help' commands if you need! [<@{ctx.message.author.id}>]")
        return

@bot.command()
async def player(ctx, choice="", playername=""):

     ## -- !player <choice> --
     ## view -> allows user to view players stats and infomation
     ## leave -> allows player to leave a team if they are in one

    if choice == "":
        await ctx.message.channel.send(f"Please enter a valid command. Use '!help' commands if you need! [<@{ctx.message.author.id}>]")
        return
    if playername == "" and choice.upper() != "LEAVE":
        await ctx.message.channel.send(f"Please mention a valid user. Use '!help' commands if you need! [<@{ctx.message.author.id}>]")
        return

    if playername != "":
        playerid_0 = playername.split("!")[1]
        playerid = playerid_0.split(">")[0]
        player = await bot.fetch_user(int(playerid))
    
    if choice.upper() in ["VIEW", "LEAVE"]:
        if choice.upper() == "VIEW":
            with open("./data/players.json", "r") as f:
                players = json.load(f)

                plr_id_str = str(player.id)

                if plr_id_str in players:
                    embed = discord.Embed(title = player.name.capitalize(), color = discord.Colour.blue())
                    embed.add_field(name = "Current Team", value = players[plr_id_str]["team"], inline = False)
                    embed.add_field(name = "Games Played", value = players[plr_id_str]["games"], inline = False)
                    embed.add_field(name = "Wins", value = players[plr_id_str]["wins"], inline = False)
                    embed.add_field(name = "Losses", value = players[plr_id_str]["losses"], inline = False)
                    await ctx.message.channel.send(embed=embed)
                else:
                    await ctx.message.channel.send(f"User <@{player.id}> does not have a profile. They need to be in a team! [<@{ctx.message.author.id}>]")
                    return

        elif choice.upper() == "LEAVE":
            with open("./data/players.json", "r") as f:
                players = json.load(f)

                plr_id_str = str(ctx.message.author.id)

                if plr_id_str in players:
                    current_team = players[plr_id_str]["team"]
                    await ctx.message.channel.send(f"You have left the team '{current_team}'! [<@{ctx.message.author.id}>]")
                    players[plr_id_str]["team"] = "N/A"
                else:
                    await ctx.message.channel.send(f"You do not currently have a profile. Join a team to get one! [<@{ctx.message.author.id}>]")
                    return

            with open("./data/players.json", "w") as f:
                json.dump(players, f)

            with open("./data/teams.json", "r") as f:
                teams = json.load(f)

                teams[current_team]["players"].remove(ctx.message.author.id)

            with open("./data/teams.json", "w") as f:
                json.dump(teams, f)

    else:
        await ctx.message.channel.send(f"That command doesnt exist. Use '!help' commands if you need! [<@{ctx.message.author.id}>]")
        return

@bot.command()
async def gb(ctx, choice="", teamname="", enemyteam=""):

    ## -- !gb <choice> --
    ## view -> allows user to view players stats and infomation
    ## leave -> allows player to leave a team if they are in one

    if choice == "":
        await ctx.message.channel.send(f"Please enter a valid command. Use '!help' commands if you need! [<@{ctx.message.author.id}>]")
        return

    if teamname == "": 
        await ctx.message.channel.send(f"Please enter a team name. Use '!help' commands if you need! [<@{ctx.message.author.id}>]")
        return

    teamname = teamname.lower()
    enemyteam = enemyteam.lower()

    if choice.upper() in ["CHALLENGE", "WAGER"]:
        if choice.upper() == "CHALLENGE":
            with open("./data/teams.json", "r") as f:
                teams = json.load(f)

                if teamname in teams:
                    if enemyteam in teams:
                        if len(teams[teamname]["players"] == 4 and len(teams[enemyteam]["players"] == 4)):
                            if teams[teamname]["owner"] == ctx.message.author.id:
                                enemy_owner = teams[enemyteam]["owner"]
                                await ctx.message.channel.send(f"<@{enemy_owner}>, your team '{enemyteam}' has been challenged. You have 60 seconds to accept, do you? [yes/no]")

                                def check(m):
                                    return m.content.upper() in ["YES", "NO"] and m.author.id == enemy_owner

                                try:
                                    msg = await bot.wait_for("message", timeout=60.0, check=check)
                                except asyncio.TimeoutError:
                                    await ctx.message.channel.send(f"The game was not accepted in time. Challenge them again or try another team! [<@{ctx.message.author.id}>]")
                                    return
                                else:
                                    if msg.content.upper() == "YES":
                                        embed = discord.Embed(title = "Challenge accepted, please report back in the next 60 minutes with scores. Use !help if you need assistance!", color = discord.Colour.blurple())
                                        
                                        ## Team 1
                                        team1_players_id = teams[teamname]["players"]
                                        team1_players = [await bot.fetch_user(playerid) for playerid in team1_players_id]
                                        team1_players_names = [player.name for player in team1_players]
                                        team1_players_str = ", ".join(team1_players_names)
                                        team1_wins = teams[teamname]["wins"]
                                        team1_losses = teams[teamname]["losses"]
                                        team1_ratio = f"{team1_wins} - {team1_losses}"
                                        team1_text = str(team1_players_str + "; " + team1_ratio)

                                        embed.add_field(name = f"Team 1: {teamname.capitalize()}", value = team1_text, inline=False)

                                        ## Team 2
                                        team2_players_id = teams[enemyteam]["players"]
                                        team2_players = [await bot.fetch_user(playerid) for playerid in team2_players_id]
                                        team2_players_names = [player.name for player in team2_players]
                                        team2_players_str = ", ".join(team2_players_names)
                                        team2_wins = teams[enemyteam]["wins"]
                                        team2_losses = teams[enemyteam]["losses"]
                                        team2_ratio = f"{team2_wins} - {team2_losses}"
                                        team2_text = str(team2_players_str + "; " + team2_ratio)

                                        embed.add_field(name = f"Team 2: {enemyteam.capitalize()}", value = team2_text, inline=False)


                                        embed.set_footer(text = f"The owner of '{teamname}': '{ctx.message.author.name}', needs to input outcome. 'Game win' or 'Game loss' in this current channel.")
                                        await ctx.message.channel.send(embed=embed)


                                        def win_check(m):
                                            return m.content.upper() in ["GAME WIN", "GAME LOSS"] and m.author.id == ctx.message.author.id

                                        try:
                                            result = await bot.wait_for("message", timeout=3600.0, check=win_check)
                                        except asyncio.TimeoutError:
                                            await ctx.message.channel.send(f"Score for game between '{teamname}' and '{enemyteam}' has not been reported. Game Aborted! [<@{ctx.message.author.id}>]")
                                        else:

                                            ## Embed for displaying game results
                                            embed = discord.Embed(title = f"Results of {teamname.capitalize()} .vs. {enemyteam.capitalize()}", color = discord.Colour.blurple())
                                            
                                            ## Team 1
                                            team1_players_id = teams[teamname]["players"]
                                            team1_players = [await bot.fetch_user(playerid) for playerid in team1_players_id]
                                            team1_players_names = [player.name for player in team1_players]
                                            team1_players_str = ", ".join(team1_players_names)
                                            


                                            ## Team 2
                                            team2_players_id = teams[enemyteam]["players"]
                                            team2_players = [await bot.fetch_user(playerid) for playerid in team2_players_id]
                                            team2_players_names = [player.name for player in team2_players]
                                            team2_players_str = ", ".join(team2_players_names)
                                            


                                            if result.content.upper() == "GAME WIN":
                                                teams[teamname]["games"] += 1
                                                teams[teamname]["wins"] += 1
                                                teams[teamname]["points"] += 100

                                                teams[enemyteam]["games"] += 1
                                                teams[enemyteam]["losses"] += 1
                                                teams[enemyteam]["points"] -= 45

                                                with open("./data/players.json", "r") as f2:
                                                    players = json.load(f2)

                                                    for playerid in teams[teamname]["players"]:
                                                        players[str(playerid)]["games"] += 1
                                                        players[str(playerid)]["wins"] += 1

                                                    for playerid in teams[enemyteam]["players"]:
                                                        players[str(playerid)]["games"] += 1
                                                        players[str(playerid)]["losses"] += 1

                                                with open("./data/players.json", "w") as f2:
                                                    json.dump(players, f2)

                                                team1_wins = teams[teamname]["wins"]
                                                team1_losses = teams[teamname]["losses"]
                                                team1_ratio = f"{team1_wins} - {team1_losses}"
                                                team1_text = str(team1_players_str + "; " + team1_ratio)

                                                team2_wins = teams[enemyteam]["wins"]
                                                team2_losses = teams[enemyteam]["losses"]
                                                team2_ratio = f"{team2_wins} - {team2_losses}"
                                                team2_text = str(team2_players_str + "; " + team2_ratio)

                                                embed.add_field(name = f"WINNERS: {teamname.capitalize()}", value = team1_text, inline=False)
                                                embed.add_field(name = f"LOSERS: {enemyteam.capitalize()}", value = team2_text, inline=False)

                                            elif result.content.upper() == "GAME LOSS":
                                                teams[enemyteam]["games"] += 1
                                                teams[enemyteam]["wins"] += 1
                                                teams[enemyteam]["points"] += 100

                                                teams[teamname]["games"] += 1
                                                teams[teamname]["losses"] += 1
                                                teams[teamname]["points"] -= 45

                                                with open("./data/players.json", "r") as f2:
                                                    players = json.load(f2)

                                                    for playerid in teams[enemyteam]["players"]:
                                                        players[str(playerid)]["games"] += 1
                                                        players[str(playerid)]["wins"] += 1

                                                    for playerid in teams[teamname]["players"]:
                                                        players[str(playerid)]["games"] += 1
                                                        players[str(playerid)]["losses"] += 1

                                                with open("./data/players.json", "w") as f2:
                                                    json.dump(players, f2)

                                                team1_wins = teams[teamname]["wins"]
                                                team1_losses = teams[teamname]["losses"]
                                                team1_ratio = f"{team1_wins} - {team1_losses}"
                                                team1_text = str(team1_players_str + "; " + team1_ratio)

                                                team2_wins = teams[enemyteam]["wins"]
                                                team2_losses = teams[enemyteam]["losses"]
                                                team2_ratio = f"{team2_wins} - {team2_losses}"
                                                team2_text = str(team2_players_str + "; " + team2_ratio)

                                                embed.add_field(name = f"LOSERS: {teamname.capitalize()}", value = team1_text, inline=False)
                                                embed.add_field(name = f"WINNERS: {enemyteam.capitalize()}", value = team2_text, inline=False)

                                            embed.set_footer(text = "Good luck in future games!")
                                            await ctx.message.channel.send(embed=embed)

                                    elif msg.content.upper() == "NO":
                                        await ctx.message.channel.send(f"Challenge declined! [<@{enemy_owner}>]")

                            else:
                                await ctx.message.channel.send(f"You are not the owner of team '{teamname}'! [<@{ctx.message.author.id}>]")
                                return
                        else:
                            if len(teams[teamname]["players"] < 4):
                                await ctx.message.channel.send(f"Team {teamname.capitalize()} does not have enough players! [<@{ctx.message.author.id}>]")
                                return
                            elif len(teams[enemyteam]["players"] < 4):
                                await ctx.message.channel.send(f"Team {enemyteam.capitalize()} does not have enough players! [<@{ctx.message.author.id}>]")
                                return
                    else:
                        await ctx.message.channel.send(f"Team '{enemyteam}' doesnt exist. You cant challenge this team! [<@{ctx.message.author.id}>]")
                        return
                else:
                    await ctx.message.channel.send(f"Team '{teamname}' doesnt exist. Create a team to start a game battle! [<@{ctx.message.author.id}>]")
                    return

            with open("./data/teams.json", "w") as f:
                json.dump(teams, f)


        elif choice.upper() == "WAGER":
            return
    
    else:
        await ctx.message.channel.send(f"That command doesnt exist. Use '!help' commands if you need! [<@{ctx.message.author.id}>]")
        return

    

bot.run(TOKEN)